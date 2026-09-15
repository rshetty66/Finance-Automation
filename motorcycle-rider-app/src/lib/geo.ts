import type { Waypoint } from "../types";

const R = 6371000;

export function haversine(a: { latitude: number; longitude: number }, b: { latitude: number; longitude: number }): number {
  const lat1 = (a.latitude * Math.PI) / 180;
  const lat2 = (b.latitude * Math.PI) / 180;
  const dLat = ((b.latitude - a.latitude) * Math.PI) / 180;
  const dLon = ((b.longitude - a.longitude) * Math.PI) / 180;

  const h = Math.sin(dLat / 2) ** 2 + Math.cos(lat1) * Math.cos(lat2) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(h), Math.sqrt(1 - h));
}

export function bearing(from: Waypoint, to: Waypoint): number {
  const lat1 = (from.latitude * Math.PI) / 180;
  const lat2 = (to.latitude * Math.PI) / 180;
  const dLon = ((to.longitude - from.longitude) * Math.PI) / 180;

  const y = Math.sin(dLon) * Math.cos(lat2);
  const x = Math.cos(lat1) * Math.sin(lat2) - Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);
  let b = (Math.atan2(y, x) * 180) / Math.PI;
  if (b < 0) b += 360;
  return b;
}

export function formatDistance(km: number, units: "metric" | "imperial" = "metric"): string {
  if (units === "imperial") {
    const mi = km * 0.621371;
    return `${mi.toFixed(mi < 10 ? 1 : 0)} mi`;
  }
  return `${km.toFixed(km < 10 ? 1 : 0)} km`;
}

export function formatSpeed(kmh: number, units: "metric" | "imperial" = "metric"): string {
  if (units === "imperial") return `${Math.round(kmh * 0.621371)} mph`;
  return `${Math.round(kmh)} km/h`;
}

export function formatDuration(sec: number): string {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}`;
  return `${m}:${String(s).padStart(2, "0")}`;
}

export function jitterRoute(start: Waypoint, end: Waypoint, seed: number, curviness: number): Waypoint[] {
  const dist = haversine(start, end);
  const numPoints = Math.max(40, Math.min(90, Math.floor(dist / 25)));
  const points: Waypoint[] = [];

  const dLat = end.latitude - start.latitude;
  const dLng = end.longitude - start.longitude;
  const spanDeg = Math.sqrt(dLat * dLat + dLng * dLng) || 0.0001;
  // Perpendicular unit vector to the start->end line.
  const perpLat = -dLng / spanDeg;
  const perpLng = dLat / spanDeg;

  const amplitude = spanDeg * 0.032 * curviness;
  const cycles = 2 + (seed % 3) + curviness * 0.7;

  for (let i = 0; i <= numPoints; i++) {
    const t = i / numPoints;
    // Ease the wobble to zero at both ends so routes start/end cleanly.
    const taper = Math.sin(t * Math.PI);
    const wobble =
      (Math.sin(t * cycles * Math.PI * 2 + seed) * 0.8 + Math.sin(t * cycles * Math.PI * 3.1 + seed * 1.9) * 0.2) *
      amplitude *
      taper;

    const baseLat = start.latitude + dLat * t;
    const baseLng = start.longitude + dLng * t;

    points.push({
      latitude: baseLat + perpLat * wobble,
      longitude: baseLng + perpLng * wobble,
      type: i === 0 ? "start" : i === numPoints ? "end" : "via",
    });
  }
  return points;
}

export function pathToSvgPoints(
  points: { latitude: number; longitude: number }[],
  width: number,
  height: number,
  padding = 12
): string {
  if (points.length === 0) return "";
  const lats = points.map((p) => p.latitude);
  const lngs = points.map((p) => p.longitude);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const latRange = maxLat - minLat || 0.0001;
  const lngRange = maxLng - minLng || 0.0001;

  return points
    .map((p) => {
      const x = padding + ((p.longitude - minLng) / lngRange) * (width - padding * 2);
      const y = height - padding - ((p.latitude - minLat) / latRange) * (height - padding * 2);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");
}
