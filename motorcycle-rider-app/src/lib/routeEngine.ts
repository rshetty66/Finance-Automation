import type { CurveAnalysis, ElevationPoint, RouteHighlight, ScoredRoute, Waypoint } from "../types";
import { bearing, haversine, jitterRoute } from "./geo";

const CURVE_THRESHOLD_DEGREES = 15;

export type RoutePreference = "curvy" | "scenic" | "balanced" | "adventure";

const ROUTE_NAMES = [
  "Ridge Line Loop", "Coastal Serpentine", "Copper Canyon Run", "Pine Summit Pass",
  "Old Mill Backroad", "Switchback Alley", "River Bend Parkway", "Granite Overlook",
];

const HIGHLIGHT_POOL: Omit<RouteHighlight, "rating">[] = [
  { type: "viewpoint", description: "Panoramic overlook, worth the stop" },
  { type: "water_crossing", description: "Scenic bridge over the river" },
  { type: "forest", description: "Shaded canopy switchbacks" },
  { type: "mountain_pass", description: "High alpine pass, big elevation swing" },
  { type: "coastal", description: "Cliffside straight with ocean views" },
  { type: "curve", description: "Technical hairpin sequence" },
];

function analyzeCurves(waypoints: Waypoint[]): CurveAnalysis {
  let total = 0, hairpin = 0, sweeping = 0, gentle = 0, maxLean = 0;

  for (let i = 2; i < waypoints.length; i++) {
    const prev = waypoints[i - 2];
    const curr = waypoints[i - 1];
    const next = waypoints[i];
    const b1 = bearing(prev, curr);
    const b2 = bearing(curr, next);
    let change = Math.abs(b2 - b1);
    if (change > 180) change = 360 - change;

    if (change >= CURVE_THRESHOLD_DEGREES) {
      total++;
      if (change > 90) hairpin++;
      else if (change > 45) sweeping++;
      else gentle++;

      const segDist = haversine(prev, curr);
      const radius = Math.max(5, segDist / (2 * Math.sin((change * Math.PI) / 360)));
      const assumedSpeed = 60;
      const lean = Math.atan((assumedSpeed * assumedSpeed) / (127 * radius)) * (180 / Math.PI);
      maxLean = Math.max(maxLean, Math.min(lean, 58));
    }
  }

  let totalDist = 0;
  for (let i = 1; i < waypoints.length; i++) totalDist += haversine(waypoints[i - 1], waypoints[i]);
  const distanceKm = totalDist / 1000;

  return {
    totalCurves: total,
    hairpinCurves: hairpin,
    sweepingCurves: sweeping,
    gentleCurves: gentle,
    maxLeanAngleRequired: maxLean,
    curveDensity: distanceKm > 0 ? total / distanceKm : 0,
  };
}

function buildElevationProfile(waypoints: Waypoint[], seed: number): ElevationPoint[] {
  let cumulative = 0;
  const base = 200 + (seed % 5) * 120;
  return waypoints.map((wp, i) => {
    if (i > 0) cumulative += haversine(waypoints[i - 1], wp);
    const elevation =
      base +
      Math.sin((i / waypoints.length) * Math.PI * 2.2 + seed) * 220 +
      Math.sin((i / waypoints.length) * Math.PI * 6 + seed * 2) * 60;
    return { distance: cumulative, elevation: Math.max(0, Math.round(elevation)) };
  });
}

function pickHighlights(seed: number, curveAnalysis: CurveAnalysis): RouteHighlight[] {
  const count = 2 + (seed % 3);
  const highlights: RouteHighlight[] = [];
  for (let i = 0; i < count; i++) {
    const pick = HIGHLIGHT_POOL[(seed + i * 3) % HIGHLIGHT_POOL.length];
    highlights.push({ ...pick, rating: 3 + ((seed + i) % 3) });
  }
  if (curveAnalysis.hairpinCurves > 3) {
    highlights.unshift({ type: "curve", description: `${curveAnalysis.hairpinCurves} hairpin sequence`, rating: 5 });
  }
  return highlights.slice(0, 4);
}

function scoreForPreference(
  preference: RoutePreference,
  curvy: number,
  scenic: number,
  difficulty: number
): number {
  switch (preference) {
    case "curvy":
      return curvy * 0.6 + scenic * 0.2 + difficulty * 0.2;
    case "scenic":
      return curvy * 0.2 + scenic * 0.6 + difficulty * 0.2;
    case "adventure":
      return curvy * 0.3 + scenic * 0.3 + difficulty * 0.4;
    default:
      return curvy * 0.35 + scenic * 0.35 + difficulty * 0.3;
  }
}

export function generateScenicRoutes(
  start: Waypoint,
  end: Waypoint,
  preference: RoutePreference,
  count = 4
): ScoredRoute[] {
  const results: ScoredRoute[] = [];
  const directDistance = haversine(start, end);

  for (let i = 0; i < count; i++) {
    const seed = i * 7 + 3;
    const curviness = 0.6 + (seed % 5) * 0.35;
    const waypoints = jitterRoute(start, end, seed, curviness);
    const curveAnalysis = analyzeCurves(waypoints);
    const elevationProfile = buildElevationProfile(waypoints, seed);
    const highlights = pickHighlights(seed, curveAnalysis);

    const distanceKm = (directDistance * (1.08 + curviness * 0.18)) / 1000;
    const durationMin = (distanceKm / (38 - curveAnalysis.curveDensity * 1.2)) * 60;

    const densityScore = Math.min(curveAnalysis.curveDensity * 20, 60);
    const qualityScore = Math.min(
      curveAnalysis.hairpinCurves * 8 + curveAnalysis.sweepingCurves * 4 + curveAnalysis.gentleCurves,
      30
    );
    const leanScore = Math.min(curveAnalysis.maxLeanAngleRequired * 2, 20);
    const curvyScore = Math.min(100, densityScore + qualityScore + leanScore);

    const elevationRange =
      Math.max(...elevationProfile.map((e) => e.elevation)) - Math.min(...elevationProfile.map((e) => e.elevation));
    const highlightScore = highlights.reduce((sum, h) => sum + h.rating * 4, 0);
    const scenicScore = Math.min(100, highlightScore + Math.min(elevationRange / 8, 30) + 15);

    const elevationDifficulty = elevationRange > 800 ? 30 : elevationRange > 400 ? 18 : 8;
    const curveDifficulty = Math.min(50, curveAnalysis.hairpinCurves * 6 + curveAnalysis.sweepingCurves * 1.5);
    const lengthDifficulty = distanceKm > 150 ? 15 : distanceKm > 80 ? 8 : 0;
    const difficultyScore = Math.min(100, curveDifficulty + elevationDifficulty + lengthDifficulty);

    const overallScore = Math.min(100, scoreForPreference(preference, curvyScore, scenicScore, difficultyScore));

    results.push({
      id: `route-${seed}-${Date.now()}`,
      name: ROUTE_NAMES[seed % ROUTE_NAMES.length],
      waypoints,
      distanceKm,
      durationMin,
      curvyScore,
      scenicScore,
      difficultyScore,
      overallScore,
      highlights,
      elevationProfile,
      curveAnalysis,
    });
  }

  return results.sort((a, b) => b.overallScore - a.overallScore);
}

export function difficultyLabel(score: number): string {
  if (score >= 70) return "Expert";
  if (score >= 45) return "Hard";
  if (score >= 22) return "Moderate";
  return "Easy";
}

export function scoreColor(score: number): string {
  if (score >= 75) return "var(--color-safe)";
  if (score >= 50) return "var(--color-accent)";
  if (score >= 25) return "var(--color-warn)";
  return "var(--color-danger)";
}
