import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  Achievement,
  CrashEvent,
  GeoPoint,
  GroupRide,
  HazardReport,
  RideHistoryEntry,
  RideSession,
  RiderProfile,
  UserPreferences,
} from "../types";
import { defaultProfile, seedAchievements, seedGroupRides, seedHazards, seedRideHistory } from "../lib/mockData";

interface AppState {
  profile: RiderProfile;
  updateProfile: (patch: Partial<RiderProfile>) => void;
  updatePreferences: (patch: Partial<UserPreferences>) => void;

  currentRide: RideSession | null;
  startRide: () => void;
  pauseRide: () => void;
  resumeRide: () => void;
  stopRide: () => void;
  appendRidePoint: (point: GeoPoint) => void;

  rideHistory: RideHistoryEntry[];
  addRideToHistory: (entry: RideHistoryEntry) => void;

  hazards: HazardReport[];
  reportHazard: (hazard: HazardReport) => void;

  achievements: Achievement[];

  groupRides: GroupRide[];

  crashEvent: CrashEvent | null;
  countdownActive: boolean;
  countdownSeconds: number;
  triggerCrash: (event: CrashEvent) => void;
  cancelCrash: () => void;
  confirmSos: () => void;
  tickCountdown: () => void;

  demoMode: boolean;
  setDemoMode: (v: boolean) => void;
}

const emptyStats = {
  distanceKm: 0,
  durationSec: 0,
  movingSec: 0,
  avgSpeed: 0,
  maxSpeed: 0,
  elevationGain: 0,
  maxLeanAngle: 0,
  hardBrakingEvents: 0,
};

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      profile: defaultProfile,
      updateProfile: (patch) => set((s) => ({ profile: { ...s.profile, ...patch } })),
      updatePreferences: (patch) =>
        set((s) => ({ profile: { ...s.profile, preferences: { ...s.profile.preferences, ...patch } } })),

      currentRide: null,
      startRide: () =>
        set({
          currentRide: {
            id: `ride-${Date.now()}`,
            status: "active",
            startedAt: new Date().toISOString(),
            path: [],
            stats: { ...emptyStats },
          },
        }),
      pauseRide: () =>
        set((s) => (s.currentRide ? { currentRide: { ...s.currentRide, status: "paused" } } : {})),
      resumeRide: () =>
        set((s) => (s.currentRide ? { currentRide: { ...s.currentRide, status: "active" } } : {})),
      stopRide: () => {
        const ride = get().currentRide;
        if (ride) {
          get().addRideToHistory({
            id: ride.id,
            name: "Free Ride",
            date: "Just now",
            distanceKm: ride.stats.distanceKm,
            durationSec: ride.stats.durationSec,
            avgSpeed: ride.stats.avgSpeed,
            maxSpeed: ride.stats.maxSpeed,
            routeTag: "Tracked",
          });
        }
        set({ currentRide: null });
      },
      appendRidePoint: (point) =>
        set((s) => {
          if (!s.currentRide || s.currentRide.status !== "active") return {};
          const path = [...s.currentRide.path, point];
          const prev = path[path.length - 2];
          let addedDistanceKm = 0;
          if (prev) {
            const R = 6371;
            const dLat = ((point.latitude - prev.latitude) * Math.PI) / 180;
            const dLon = ((point.longitude - prev.longitude) * Math.PI) / 180;
            const lat1 = (prev.latitude * Math.PI) / 180;
            const lat2 = (point.latitude * Math.PI) / 180;
            const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
            addedDistanceKm = R * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
          }
          const speed = point.speed ?? 0;
          const distanceKm = s.currentRide.stats.distanceKm + addedDistanceKm;
          const durationSec = (Date.now() - new Date(s.currentRide.startedAt).getTime()) / 1000;
          const speeds = [...path.map((p) => p.speed ?? 0)];
          const maxSpeed = Math.max(s.currentRide.stats.maxSpeed, speed);
          const avgSpeed = durationSec > 0 ? distanceKm / (durationSec / 3600) : 0;
          void speeds;
          return {
            currentRide: {
              ...s.currentRide,
              path,
              stats: {
                ...s.currentRide.stats,
                distanceKm,
                durationSec,
                movingSec: speed > 3 ? s.currentRide.stats.movingSec + 1 : s.currentRide.stats.movingSec,
                avgSpeed,
                maxSpeed,
              },
            },
          };
        }),

      rideHistory: seedRideHistory,
      addRideToHistory: (entry) => set((s) => ({ rideHistory: [entry, ...s.rideHistory] })),

      hazards: seedHazards,
      reportHazard: (hazard) => set((s) => ({ hazards: [hazard, ...s.hazards] })),

      achievements: seedAchievements,

      groupRides: seedGroupRides,

      crashEvent: null,
      countdownActive: false,
      countdownSeconds: 30,
      triggerCrash: (event) =>
        set({ crashEvent: event, countdownActive: true, countdownSeconds: get().profile.preferences.sosCountdownSeconds }),
      cancelCrash: () =>
        set((s) => ({
          countdownActive: false,
          crashEvent: s.crashEvent ? { ...s.crashEvent, status: "false_alarm" } : null,
        })),
      confirmSos: () =>
        set((s) => ({
          countdownActive: false,
          crashEvent: s.crashEvent ? { ...s.crashEvent, status: "confirmed" } : null,
        })),
      tickCountdown: () =>
        set((s) => {
          if (!s.countdownActive) return {};
          const next = s.countdownSeconds - 1;
          if (next <= 0) {
            return { countdownSeconds: 0, countdownActive: false, crashEvent: s.crashEvent ? { ...s.crashEvent, status: "confirmed" } : null };
          }
          return { countdownSeconds: next };
        }),

      demoMode: true,
      setDemoMode: (v) => set({ demoMode: v }),
    }),
    {
      name: "rideout-storage",
      partialize: (s) => ({
        profile: s.profile,
        rideHistory: s.rideHistory,
        hazards: s.hazards,
        achievements: s.achievements,
      }),
    }
  )
);
