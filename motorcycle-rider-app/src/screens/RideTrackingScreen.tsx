import { useEffect, useRef, useState } from "react";
import { Play, Pause, Square, Gauge, Mountain, Timer, TriangleAlert, LocateFixed } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, StatTile, PrimaryButton, Badge } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import { formatDistance, formatDuration, formatSpeed, pathToSvgPoints } from "../lib/geo";
import { nextSimulatedPoint } from "../lib/rideSimulator";

export function RideTrackingScreen() {
  const currentRide = useAppStore((s) => s.currentRide);
  const startRide = useAppStore((s) => s.startRide);
  const pauseRide = useAppStore((s) => s.pauseRide);
  const resumeRide = useAppStore((s) => s.resumeRide);
  const stopRide = useAppStore((s) => s.stopRide);
  const appendRidePoint = useAppStore((s) => s.appendRidePoint);
  const units = useAppStore((s) => s.profile.preferences.units);

  const tickRef = useRef(0);
  const gpsLiveRef = useRef(false);
  const [gpsLive, setGpsLive] = useState(false);
  const [leanAngle, setLeanAngle] = useState(0);

  useEffect(() => {
    if (!currentRide || currentRide.status !== "active") return;

    let watchId: number | null = null;

    if ("geolocation" in navigator) {
      watchId = navigator.geolocation.watchPosition(
        (pos) => {
          gpsLiveRef.current = true;
          setGpsLive(true);
          appendRidePoint({
            latitude: pos.coords.latitude,
            longitude: pos.coords.longitude,
            altitude: pos.coords.altitude ?? undefined,
            speed: (pos.coords.speed ?? 0) * 3.6,
            heading: pos.coords.heading ?? undefined,
            timestamp: pos.timestamp,
          });
        },
        () => {
          gpsLiveRef.current = false;
          setGpsLive(false);
        },
        { enableHighAccuracy: true, maximumAge: 1000 }
      );
    }

    const interval = setInterval(() => {
      if (!gpsLiveRef.current) {
        tickRef.current += 1;
        const state = useAppStore.getState().currentRide;
        const last = state?.path[state.path.length - 1] ?? null;
        appendRidePoint(nextSimulatedPoint(last, tickRef.current));
      }
      setLeanAngle(Math.abs(Math.sin(tickRef.current * 0.3)) * 38);
    }, 1000);

    return () => {
      if (watchId !== null) navigator.geolocation.clearWatch(watchId);
      clearInterval(interval);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentRide?.status]);

  const isIdle = !currentRide;
  const isActive = currentRide?.status === "active";
  const isPaused = currentRide?.status === "paused";
  const stats = currentRide?.stats;
  const svgPoints = currentRide ? pathToSvgPoints(currentRide.path, 400, 220) : "";

  return (
    <div>
      <TopBar title="Ride Tracker" />

      <div className="px-4 pt-4 space-y-4">
        <Card className="overflow-hidden">
          <div className="relative h-56 bg-[var(--color-surface-2)]">
            <svg viewBox="0 0 400 220" className="w-full h-full">
              <defs>
                <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
                  <path d="M 20 0 L 0 0 0 20" fill="none" stroke="var(--color-border)" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="400" height="220" fill="url(#grid)" />
              {svgPoints && (
                <polyline points={svgPoints} fill="none" stroke="var(--color-accent)" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />
              )}
              {svgPoints && (
                <circle
                  cx={svgPoints.split(" ").pop()?.split(",")[0]}
                  cy={svgPoints.split(" ").pop()?.split(",")[1]}
                  r="6"
                  fill="var(--color-accent)"
                  stroke="#0A0A0A"
                  strokeWidth="2"
                />
              )}
            </svg>
            {isIdle && (
              <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-[var(--color-ink-faint)]">
                <LocateFixed size={28} />
                <p className="text-sm">Your live route draws here</p>
              </div>
            )}
            <div className="absolute top-3 right-3">
              <Badge tone={gpsLive ? "safe" : "default"}>{gpsLive ? "GPS live" : isIdle ? "Ready" : "Simulated GPS"}</Badge>
            </div>
          </div>
        </Card>

        <div className="text-center py-2">
          <p className="text-[var(--color-ink-faint)] text-xs uppercase tracking-widest font-semibold mb-1">Current speed</p>
          <div className="flex items-baseline justify-center gap-2">
            <span className="font-display text-6xl font-extrabold tabular-nums">
              {Math.round((currentRide?.path[currentRide.path.length - 1]?.speed ?? 0))}
            </span>
            <span className="text-lg text-[var(--color-ink-dim)]">{units === "imperial" ? "mph" : "km/h"}</span>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <StatTile label="Distance" value={formatDistance(stats?.distanceKm ?? 0, units).split(" ")[0]} unit={units === "imperial" ? "mi" : "km"} icon={<Gauge size={13} />} />
          <StatTile label="Duration" value={formatDuration(stats?.durationSec ?? 0)} icon={<Timer size={13} />} />
          <StatTile label="Lean angle" value={Math.round(isActive ? leanAngle : 0)} unit="°" icon={<Mountain size={13} />} />
        </div>

        <div className="grid grid-cols-2 gap-3">
          <StatTile label="Avg speed" value={formatSpeed(stats?.avgSpeed ?? 0, units).split(" ")[0]} unit={units === "imperial" ? "mph" : "km/h"} />
          <StatTile label="Top speed" value={formatSpeed(stats?.maxSpeed ?? 0, units).split(" ")[0]} unit={units === "imperial" ? "mph" : "km/h"} />
        </div>

        {leanAngle > 32 && isActive && (
          <Card className="p-3 flex items-center gap-2 border-[var(--color-warn)]">
            <TriangleAlert size={16} className="text-[var(--color-warn)] shrink-0" />
            <p className="text-xs text-[var(--color-ink-dim)]">Aggressive lean angle detected — ride within your limits.</p>
          </Card>
        )}

        <div className="pt-2 pb-4">
          {isIdle && (
            <PrimaryButton className="w-full h-14 text-base" onClick={startRide}>
              <Play size={18} fill="currentColor" /> Start Ride
            </PrimaryButton>
          )}
          {(isActive || isPaused) && (
            <div className="flex gap-3">
              {isActive ? (
                <PrimaryButton tone="neutral" className="flex-1 h-14" onClick={pauseRide}>
                  <Pause size={18} /> Pause
                </PrimaryButton>
              ) : (
                <PrimaryButton className="flex-1 h-14" onClick={resumeRide}>
                  <Play size={18} fill="currentColor" /> Resume
                </PrimaryButton>
              )}
              <PrimaryButton tone="danger" className="flex-1 h-14" onClick={stopRide}>
                <Square size={16} fill="currentColor" /> Stop
              </PrimaryButton>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
