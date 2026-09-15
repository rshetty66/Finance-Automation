export interface GeoPoint {
  latitude: number;
  longitude: number;
  altitude?: number;
  speed?: number; // km/h
  heading?: number; // degrees
  timestamp: number;
}

export interface Motorcycle {
  make: string;
  model: string;
  year: number;
  color: string;
  engineSize?: number;
  fuelType: "petrol" | "diesel" | "electric";
}

export interface SafetyContact {
  id: string;
  name: string;
  phone: string;
  relationship: string;
  notifyOnCrash: boolean;
  notifyOnRideStart: boolean;
}

export interface UserPreferences {
  units: "metric" | "imperial";
  routeType: "fastest" | "curvy" | "scenic" | "offroad";
  avoidHighways: boolean;
  crashDetectionEnabled: boolean;
  crashDetectionSensitivity: "low" | "medium" | "high";
  sosCountdownSeconds: number;
  showHazardAlerts: boolean;
}

export interface RiderProfile {
  displayName: string;
  avatarEmoji: string;
  motorcycle: Motorcycle;
  safetyContacts: SafetyContact[];
  preferences: UserPreferences;
  memberSince: string;
}

export type HazardType =
  | "pothole"
  | "gravel"
  | "debris"
  | "accident"
  | "construction"
  | "ice"
  | "animals"
  | "sharp_curve"
  | "police"
  | "slippery_surface";

export interface HazardReport {
  id: string;
  type: HazardType;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  distanceKm: number;
  reportedAt: string;
  verifiedCount: number;
}

export interface Waypoint {
  latitude: number;
  longitude: number;
  type: "start" | "end" | "via";
}

export interface RouteHighlight {
  type: "curve" | "viewpoint" | "water_crossing" | "forest" | "mountain_pass" | "coastal";
  description: string;
  rating: number;
}

export interface CurveAnalysis {
  totalCurves: number;
  hairpinCurves: number;
  sweepingCurves: number;
  gentleCurves: number;
  maxLeanAngleRequired: number;
  curveDensity: number;
}

export interface ElevationPoint {
  distance: number;
  elevation: number;
}

export interface ScoredRoute {
  id: string;
  name: string;
  waypoints: Waypoint[];
  distanceKm: number;
  durationMin: number;
  curvyScore: number;
  scenicScore: number;
  difficultyScore: number;
  overallScore: number;
  highlights: RouteHighlight[];
  elevationProfile: ElevationPoint[];
  curveAnalysis: CurveAnalysis;
}

export interface RideStats {
  distanceKm: number;
  durationSec: number;
  movingSec: number;
  avgSpeed: number;
  maxSpeed: number;
  elevationGain: number;
  maxLeanAngle: number;
  hardBrakingEvents: number;
}

export type RideStatus = "idle" | "active" | "paused" | "completed";

export interface RideSession {
  id: string;
  status: RideStatus;
  startedAt: string;
  endedAt?: string;
  path: GeoPoint[];
  stats: RideStats;
}

export interface RideHistoryEntry {
  id: string;
  name: string;
  date: string;
  distanceKm: number;
  durationSec: number;
  avgSpeed: number;
  maxSpeed: number;
  routeTag: string;
}

export interface CrashEvent {
  id: string;
  timestamp: string;
  severity: "minor" | "moderate" | "severe" | "critical";
  impactForce: number;
  status: "countdown" | "confirmed" | "false_alarm";
}

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  tier: "bronze" | "silver" | "gold" | "platinum";
  progress: number;
  target: number;
  unlockedAt?: string;
}

export interface GroupMember {
  id: string;
  name: string;
  avatarEmoji: string;
  role: "leader" | "sweep" | "member";
  isRiding: boolean;
}

export interface GroupRide {
  id: string;
  name: string;
  scheduledFor: string;
  meetPoint: string;
  members: GroupMember[];
  distanceKm: number;
  status: "planning" | "active" | "completed";
}
