import { useNavigate } from "react-router-dom";
import {
  Flame, MapPinned, ShieldAlert, TriangleAlert, Users, Trophy,
  CloudSun, Wind, Droplets, ChevronRight, Gauge,
} from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, SectionHeader, StatTile, Badge, PrimaryButton } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import { formatDistance, formatDuration, formatSpeed } from "../lib/geo";
import { weeklyDistanceKm } from "../lib/mockData";

const DAY_LABELS = ["M", "T", "W", "T", "F", "S", "S"];

export function DashboardScreen() {
  const navigate = useNavigate();
  const profile = useAppStore((s) => s.profile);
  const rideHistory = useAppStore((s) => s.rideHistory);
  const hazards = useAppStore((s) => s.hazards);
  const achievements = useAppStore((s) => s.achievements);
  const currentRide = useAppStore((s) => s.currentRide);
  const units = profile.preferences.units;

  const totalDistance = rideHistory.reduce((sum, r) => sum + r.distanceKm, 0);
  const totalDuration = rideHistory.reduce((sum, r) => sum + r.durationSec, 0);
  const maxWeekly = Math.max(...weeklyDistanceKm, 1);
  const nextAchievement = achievements.find((a) => !a.unlockedAt);
  const topHazards = hazards.slice(0, 2);

  return (
    <div>
      <TopBar
        title="RideOut"
        action={
          <button
            onClick={() => navigate("/profile")}
            className="w-9 h-9 rounded-full bg-[var(--color-surface-2)] flex items-center justify-center text-lg"
            aria-label="Profile"
          >
            {profile.avatarEmoji}
          </button>
        }
      />

      <div className="px-4 pt-4 space-y-5">
        <div>
          <p className="text-[var(--color-ink-dim)] text-sm">Welcome back,</p>
          <h2 className="font-display text-3xl font-bold">{profile.displayName.split(" ")[0]}</h2>
        </div>

        {currentRide ? (
          <Card className="p-4 border-[var(--color-accent)] bg-gradient-to-br from-[var(--color-accent-soft)] to-transparent">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="relative flex h-2.5 w-2.5">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[var(--color-accent)] opacity-75" />
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-[var(--color-accent)]" />
                </span>
                <span className="font-display font-semibold uppercase tracking-wide text-sm">Ride in progress</span>
              </div>
              <span className="tabular-nums text-sm text-[var(--color-ink-dim)]">
                {formatDuration(currentRide.stats.durationSec)}
              </span>
            </div>
            <PrimaryButton className="w-full mt-3" onClick={() => navigate("/ride")}>
              <Gauge size={16} /> Open ride tracker
            </PrimaryButton>
          </Card>
        ) : (
          <PrimaryButton className="w-full" onClick={() => navigate("/ride")}>
            <Gauge size={16} /> Start a ride
          </PrimaryButton>
        )}

        <Card className="p-4">
          <div className="flex items-center gap-2 text-[var(--color-ink-dim)] text-sm mb-3">
            <CloudSun size={18} className="text-[var(--color-warn)]" />
            <span>Riding conditions look great right now</span>
          </div>
          <div className="flex items-center justify-between">
            <div className="flex items-baseline gap-1">
              <span className="font-display text-3xl font-bold">21°C</span>
              <span className="text-xs text-[var(--color-ink-dim)]">Clear</span>
            </div>
            <div className="flex gap-4 text-xs text-[var(--color-ink-dim)]">
              <div className="flex items-center gap-1">
                <Wind size={14} /> 12 km/h
              </div>
              <div className="flex items-center gap-1">
                <Droplets size={14} /> 8%
              </div>
            </div>
          </div>
        </Card>

        <div>
          <SectionHeader title="This week" />
          <Card className="p-4">
            <div className="flex items-end justify-between gap-2 h-24 mb-2">
              {weeklyDistanceKm.map((km, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-1.5 h-full justify-end">
                  <div
                    className="w-full rounded-md"
                    style={{
                      height: `${Math.max(6, (km / maxWeekly) * 100)}%`,
                      backgroundColor: km > 0 ? "var(--color-accent)" : "var(--color-surface-2)",
                    }}
                  />
                  <span className="text-[10px] text-[var(--color-ink-faint)]">{DAY_LABELS[i]}</span>
                </div>
              ))}
            </div>
            <div className="flex justify-between pt-2 border-t border-[var(--color-border)] text-xs text-[var(--color-ink-dim)]">
              <span>{formatDistance(weeklyDistanceKm.reduce((a, b) => a + b, 0), units)} this week</span>
              <span className="text-[var(--color-safe)] font-semibold">+18% vs last week</span>
            </div>
          </Card>
        </div>

        <div className="grid grid-cols-2 gap-3">
          <StatTile label="Total distance" value={formatDistance(totalDistance, units).split(" ")[0]} unit={units === "imperial" ? "mi" : "km"} icon={<Flame size={14} />} />
          <StatTile label="Time in the saddle" value={formatDuration(totalDuration)} icon={<Gauge size={14} />} />
        </div>

        <div>
          <SectionHeader
            title="Nearby hazards"
            action={
              <button onClick={() => navigate("/hazards")} className="text-xs font-semibold text-[var(--color-accent)] flex items-center gap-0.5">
                View all <ChevronRight size={14} />
              </button>
            }
          />
          <div className="space-y-2">
            {topHazards.map((h) => (
              <Card key={h.id} className="p-3 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-[#ff4b4b1a] flex items-center justify-center shrink-0">
                  <TriangleAlert size={17} className="text-[var(--color-danger)]" />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium truncate">{h.description}</p>
                  <p className="text-xs text-[var(--color-ink-faint)]">{h.distanceKm} km ahead · {h.reportedAt}</p>
                </div>
                <Badge tone={h.severity === "high" || h.severity === "critical" ? "danger" : "warn"}>{h.severity}</Badge>
              </Card>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-3 gap-3">
          <QuickAction icon={MapPinned} label="Routes" onClick={() => navigate("/routes")} />
          <QuickAction icon={Users} label="Group Rides" onClick={() => navigate("/group-rides")} />
          <QuickAction icon={ShieldAlert} label="Safety" onClick={() => navigate("/safety")} />
        </div>

        {nextAchievement && (
          <Card className="p-4 flex items-center gap-3" onClick={() => navigate("/achievements")}>
            <div className="w-11 h-11 rounded-xl bg-[var(--color-accent-soft)] flex items-center justify-center text-xl shrink-0">
              {nextAchievement.icon}
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5 text-[var(--color-ink-faint)] text-[11px] uppercase font-semibold tracking-wide mb-0.5">
                <Trophy size={12} /> Next achievement
              </div>
              <p className="text-sm font-medium truncate">{nextAchievement.name}</p>
              <div className="h-1.5 rounded-full bg-[var(--color-surface-2)] mt-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-[var(--color-accent)]"
                  style={{ width: `${(nextAchievement.progress / nextAchievement.target) * 100}%` }}
                />
              </div>
            </div>
            <ChevronRight size={18} className="text-[var(--color-ink-faint)] shrink-0" />
          </Card>
        )}

        <div className="pt-2">
          <SectionHeader
            title="Recent rides"
            action={
              <button onClick={() => navigate("/history")} className="text-xs font-semibold text-[var(--color-accent)] flex items-center gap-0.5">
                View all <ChevronRight size={14} />
              </button>
            }
          />
          <div className="space-y-2">
            {rideHistory.slice(0, 3).map((r) => (
              <Card key={r.id} className="p-3 flex items-center justify-between">
                <div className="min-w-0">
                  <p className="text-sm font-medium truncate">{r.name}</p>
                  <p className="text-xs text-[var(--color-ink-faint)]">{r.date} · {formatDistance(r.distanceKm, units)}</p>
                </div>
                <span className="text-xs font-semibold text-[var(--color-ink-dim)] tabular-nums">
                  {formatSpeed(r.avgSpeed, units)} avg
                </span>
              </Card>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function QuickAction({ icon: Icon, label, onClick }: { icon: typeof MapPinned; label: string; onClick: () => void }) {
  return (
    <button onClick={onClick} className="flex flex-col items-center gap-2 py-3">
      <div className="w-12 h-12 rounded-2xl bg-[var(--color-surface)] border border-[var(--color-border)] flex items-center justify-center">
        <Icon size={20} className="text-[var(--color-accent)]" />
      </div>
      <span className="text-[11px] text-[var(--color-ink-dim)] font-medium text-center">{label}</span>
    </button>
  );
}
