import { useState } from "react";
import {
  Search, RouteIcon, Image, Scale, Mountain, MapPin, Clock, Sigma,
  ChevronLeft, Navigation, Star,
} from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, Pill, ScoreBar, PrimaryButton, Badge } from "../components/ui";
import { generateScenicRoutes, difficultyLabel, scoreColor, type RoutePreference } from "../lib/routeEngine";
import type { ScoredRoute } from "../types";
import { formatDistance, pathToSvgPoints } from "../lib/geo";
import { useAppStore } from "../store/useAppStore";
import { useNavigate } from "react-router-dom";

const PREFERENCES: { key: RoutePreference; icon: typeof RouteIcon; label: string; desc: string }[] = [
  { key: "curvy", icon: RouteIcon, label: "Curvy", desc: "Max twisties" },
  { key: "scenic", icon: Image, label: "Scenic", desc: "Best views" },
  { key: "balanced", icon: Scale, label: "Balanced", desc: "Best of both" },
  { key: "adventure", icon: Mountain, label: "Adventure", desc: "Push your limits" },
];

const START = { latitude: 37.7749, longitude: -122.4194, type: "start" as const };
const END = { latitude: 38.05, longitude: -122.75, type: "end" as const };

export function ScenicRoutesScreen() {
  const [preference, setPreference] = useState<RoutePreference>("balanced");
  const [filter, setFilter] = useState<"all" | "curvy" | "scenic" | "easy">("all");
  const [routes, setRoutes] = useState<ScoredRoute[]>(() => generateScenicRoutes(START, END, "balanced"));
  const [selected, setSelected] = useState<ScoredRoute | null>(null);
  const [loading, setLoading] = useState(false);

  const discover = (pref: RoutePreference) => {
    setPreference(pref);
    setLoading(true);
    setTimeout(() => {
      setRoutes(generateScenicRoutes(START, END, pref));
      setLoading(false);
    }, 450);
  };

  const filtered = routes.filter((r) => {
    if (filter === "curvy") return r.curvyScore > 55;
    if (filter === "scenic") return r.scenicScore > 55;
    if (filter === "easy") return r.difficultyScore < 35;
    return true;
  });

  if (selected) return <RouteDetail route={selected} onBack={() => setSelected(null)} />;

  return (
    <div>
      <TopBar title="Scenic Routes" />

      <div className="px-4 pt-4 space-y-4">
        <div className="flex items-center gap-2 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-xl px-3 py-2.5">
          <Search size={17} className="text-[var(--color-ink-faint)]" />
          <input
            placeholder="Where do you want to ride?"
            className="bg-transparent flex-1 outline-none text-sm placeholder:text-[var(--color-ink-faint)]"
          />
        </div>

        <div className="flex gap-2 overflow-x-auto pb-1 -mx-4 px-4">
          {PREFERENCES.map((p) => {
            const Icon = p.icon;
            const active = preference === p.key;
            return (
              <button
                key={p.key}
                onClick={() => discover(p.key)}
                className="flex flex-col items-center gap-1 min-w-[86px] rounded-xl px-3 py-2.5 border"
                style={{
                  borderColor: active ? "var(--color-accent)" : "var(--color-border)",
                  backgroundColor: active ? "var(--color-accent-soft)" : "var(--color-surface)",
                }}
              >
                <Icon size={20} className={active ? "text-[var(--color-accent)]" : "text-[var(--color-ink-faint)]"} />
                <span className={`text-xs font-semibold ${active ? "text-[var(--color-accent)]" : "text-[var(--color-ink-dim)]"}`}>{p.label}</span>
                <span className="text-[10px] text-[var(--color-ink-faint)]">{p.desc}</span>
              </button>
            );
          })}
        </div>

        <div className="flex gap-2">
          {(["all", "curvy", "scenic", "easy"] as const).map((f) => (
            <Pill key={f} active={filter === f} onClick={() => setFilter(f)}>
              {f[0].toUpperCase() + f.slice(1)}
            </Pill>
          ))}
        </div>

        {loading ? (
          <div className="space-y-3">
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton h-32 rounded-2xl" />
            ))}
          </div>
        ) : (
          <div className="space-y-3 pb-4">
            {filtered.map((route, i) => (
              <RouteCard key={route.id} route={route} rank={i + 1} onOpen={() => setSelected(route)} />
            ))}
            {filtered.length === 0 && (
              <div className="text-center py-16 text-[var(--color-ink-faint)]">
                <MapPin size={36} className="mx-auto mb-2" />
                <p className="text-sm">No routes match this filter</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function RouteCard({ route, rank, onOpen }: { route: ScoredRoute; rank: number; onOpen: () => void }) {
  const units = useAppStore((s) => s.profile.preferences.units);
  return (
    <Card className="p-4 relative border-l-4 !border-l-[var(--color-accent)]" onClick={onOpen}>
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-full bg-[var(--color-accent)] text-[#160900] flex items-center justify-center text-xs font-bold shrink-0">
          {rank}
        </div>
        <div className="flex-1 min-w-0 pr-10">
          <h3 className="font-display font-bold text-base mb-2 truncate">{route.name}</h3>
          <div className="flex gap-3 mb-2">
            <ScoreBar label="Curvy" score={route.curvyScore} color="var(--color-accent)" />
            <ScoreBar label="Scenic" score={route.scenicScore} color="var(--color-safe)" />
            <ScoreBar label="Hard" score={route.difficultyScore} color="var(--color-danger)" />
          </div>
          <div className="flex flex-wrap gap-x-3 gap-y-1 text-[11px] text-[var(--color-ink-dim)]">
            <span className="flex items-center gap-1"><MapPin size={11} /> {formatDistance(route.distanceKm, units)}</span>
            <span className="flex items-center gap-1"><Clock size={11} /> {Math.round(route.durationMin)} min</span>
            <span className="flex items-center gap-1"><Sigma size={11} /> {route.curveAnalysis.totalCurves} curves</span>
          </div>
          {route.highlights.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-2">
              {route.highlights.slice(0, 2).map((h, i) => (
                <span key={i} className="px-2 py-0.5 rounded-md bg-[var(--color-surface-2)] text-[10px] text-[var(--color-ink-dim)]">
                  {h.description}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>
      <div
        className="absolute top-4 right-4 w-11 h-11 rounded-full flex flex-col items-center justify-center"
        style={{ backgroundColor: scoreColor(route.overallScore) }}
      >
        <span className="text-[#0A0A0A] font-bold text-sm leading-none">{Math.round(route.overallScore)}</span>
      </div>
    </Card>
  );
}

function RouteDetail({ route, onBack }: { route: ScoredRoute; onBack: () => void }) {
  const navigate = useNavigate();
  const units = useAppStore((s) => s.profile.preferences.units);
  const startRide = useAppStore((s) => s.startRide);
  const svgPoints = pathToSvgPoints(route.waypoints, 400, 200);
  const maxElev = Math.max(...route.elevationProfile.map((e) => e.elevation));
  const minElev = Math.min(...route.elevationProfile.map((e) => e.elevation));
  const elevRange = Math.max(1, maxElev - minElev);
  const elevPoints = route.elevationProfile
    .map((e, i) => {
      const x = (i / (route.elevationProfile.length - 1)) * 400;
      const y = 100 - ((e.elevation - minElev) / elevRange) * 90;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div>
      <header className="sticky top-0 z-30 safe-top bg-[#08090bee] backdrop-blur-md border-b border-[var(--color-border)]">
        <div className="flex items-center gap-2 px-4 h-14">
          <button onClick={onBack} className="-ml-1.5 p-1.5 rounded-full active:bg-[var(--color-surface-2)]">
            <ChevronLeft size={22} />
          </button>
          <h1 className="font-display text-xl font-bold uppercase tracking-wide truncate">{route.name}</h1>
        </div>
      </header>

      <div className="px-4 pt-4 space-y-4 pb-4">
        <Card className="overflow-hidden">
          <svg viewBox="0 0 400 200" className="w-full h-48 bg-[var(--color-surface-2)]">
            <polyline points={svgPoints} fill="none" stroke="var(--color-accent)" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
            {route.waypoints
              .filter((_, i) => i % Math.max(1, Math.floor(route.waypoints.length / 6)) === 0)
              .map((_, i) => {
                const idx = i * Math.max(1, Math.floor(route.waypoints.length / 6));
                const pts = svgPoints.split(" ");
                const p = pts[Math.min(idx, pts.length - 1)]?.split(",");
                if (!p) return null;
                return <circle key={i} cx={p[0]} cy={p[1]} r="3" fill="var(--color-ink)" opacity={0.5} />;
              })}
          </svg>
        </Card>

        <div className="grid grid-cols-3 gap-2">
          <MiniStat value={formatDistance(route.distanceKm, units).split(" ")[0]} label={units === "imperial" ? "mi" : "km"} />
          <MiniStat value={String(Math.round(route.durationMin))} label="min" />
          <MiniStat value={String(Math.round(maxElev - minElev))} label="elev m" />
          <MiniStat value={String(route.curveAnalysis.totalCurves)} label="curves" />
          <MiniStat value={`${Math.round(route.curveAnalysis.maxLeanAngleRequired)}°`} label="max lean" />
          <MiniStat value={route.curveAnalysis.curveDensity.toFixed(1)} label="curves/km" />
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold uppercase tracking-wide mb-2">Elevation profile</h2>
          <Card className="p-3">
            <svg viewBox="0 0 400 100" className="w-full h-24">
              <polyline points={`0,100 ${elevPoints} 400,100`} fill="var(--color-accent-soft)" stroke="none" />
              <polyline points={elevPoints} fill="none" stroke="var(--color-accent)" strokeWidth="2.5" />
            </svg>
          </Card>
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold uppercase tracking-wide mb-2">Curve breakdown</h2>
          <div className="grid grid-cols-2 gap-2">
            <CurveStat label="Hairpins" value={route.curveAnalysis.hairpinCurves} color="var(--color-danger)" />
            <CurveStat label="Sweeping" value={route.curveAnalysis.sweepingCurves} color="var(--color-warn)" />
            <CurveStat label="Gentle" value={route.curveAnalysis.gentleCurves} color="var(--color-safe)" />
            <CurveStat label="Difficulty" value={difficultyLabel(route.difficultyScore)} color="var(--color-accent)" />
          </div>
        </div>

        <div>
          <h2 className="font-display text-lg font-semibold uppercase tracking-wide mb-2">Highlights</h2>
          <div className="space-y-2">
            {route.highlights.map((h, i) => (
              <Card key={i} className="p-3 flex items-center gap-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium">{h.description}</p>
                  <div className="flex gap-0.5 mt-1">
                    {[1, 2, 3, 4, 5].map((s) => (
                      <Star key={s} size={12} fill={s <= h.rating ? "var(--color-warn)" : "none"} stroke="var(--color-warn)" />
                    ))}
                  </div>
                </div>
                <Badge>{h.type.replace("_", " ")}</Badge>
              </Card>
            ))}
          </div>
        </div>

        <PrimaryButton className="w-full h-14" onClick={() => { startRide(); navigate("/ride"); }}>
          <Navigation size={18} /> Start this route
        </PrimaryButton>
      </div>
    </div>
  );
}

function MiniStat({ value, label }: { value: string; label: string }) {
  return (
    <Card className="p-2.5 flex flex-col items-center">
      <span className="font-display text-lg font-bold tabular-nums">{value}</span>
      <span className="text-[10px] text-[var(--color-ink-faint)]">{label}</span>
    </Card>
  );
}

function CurveStat({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <Card className="p-3 flex flex-col items-center gap-0.5">
      <span className="font-display text-xl font-bold" style={{ color }}>{value}</span>
      <span className="text-[10px] text-[var(--color-ink-faint)]">{label}</span>
    </Card>
  );
}
