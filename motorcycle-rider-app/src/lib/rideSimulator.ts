import type { GeoPoint } from "../types";

const ORIGIN = { latitude: 37.7749, longitude: -122.4194 };

export function nextSimulatedPoint(prev: GeoPoint | null, tick: number): GeoPoint {
  const t = tick * 0.04;
  const speedWave = 45 + Math.sin(t * 0.6) * 35 + Math.sin(t * 2.3) * 8;
  const speed = Math.max(0, speedWave);

  const base = prev ?? { ...ORIGIN, timestamp: Date.now() };
  const heading = (t * 14) % 360;
  const metersPerTick = (speed / 3.6) * 1;
  const dLat = (metersPerTick * Math.cos((heading * Math.PI) / 180)) / 111320;
  const dLon =
    (metersPerTick * Math.sin((heading * Math.PI) / 180)) / (111320 * Math.cos((base.latitude * Math.PI) / 180));

  return {
    latitude: base.latitude + dLat,
    longitude: base.longitude + dLon,
    altitude: 30 + Math.sin(t * 0.3) * 40,
    speed,
    heading,
    timestamp: Date.now(),
  };
}
