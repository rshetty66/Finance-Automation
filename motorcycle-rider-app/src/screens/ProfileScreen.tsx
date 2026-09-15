import { useNavigate } from "react-router-dom";
import { Bike, Trophy, Users, History, Ruler, Route as RouteIcon, ChevronRight, ShieldAlert } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, SectionHeader, Pill } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import { formatDistance } from "../lib/geo";

export function ProfileScreen() {
  const navigate = useNavigate();
  const profile = useAppStore((s) => s.profile);
  const updatePreferences = useAppStore((s) => s.updatePreferences);
  const rideHistory = useAppStore((s) => s.rideHistory);
  const achievements = useAppStore((s) => s.achievements);
  const units = profile.preferences.units;
  const totalDistance = rideHistory.reduce((sum, r) => sum + r.distanceKm, 0);
  const unlockedCount = achievements.filter((a) => a.unlockedAt).length;

  return (
    <div>
      <TopBar title="Profile" />

      <div className="px-4 pt-4 space-y-5 pb-4">
        <Card className="p-4 flex items-center gap-4">
          <div className="w-16 h-16 rounded-2xl bg-[var(--color-accent-soft)] flex items-center justify-center text-3xl">
            {profile.avatarEmoji}
          </div>
          <div className="flex-1 min-w-0">
            <h2 className="font-display text-xl font-bold truncate">{profile.displayName}</h2>
            <p className="text-xs text-[var(--color-ink-faint)]">
              Riding since {new Date(profile.memberSince).getFullYear()}
            </p>
          </div>
        </Card>

        <div className="grid grid-cols-3 gap-3">
          <StatChip value={formatDistance(totalDistance, units)} label="Total distance" />
          <StatChip value={String(rideHistory.length)} label="Rides logged" />
          <StatChip value={`${unlockedCount}/${achievements.length}`} label="Badges" />
        </div>

        <Card className="p-4">
          <div className="flex items-center gap-3 mb-3">
            <Bike size={20} className="text-[var(--color-accent)]" />
            <h3 className="font-display font-semibold uppercase tracking-wide text-sm">Motorcycle</h3>
          </div>
          <p className="font-semibold">{profile.motorcycle.year} {profile.motorcycle.make} {profile.motorcycle.model}</p>
          <p className="text-xs text-[var(--color-ink-faint)] mt-0.5">
            {profile.motorcycle.color} · {profile.motorcycle.engineSize}cc · {profile.motorcycle.fuelType}
          </p>
        </Card>

        <div>
          <SectionHeader title="Quick links" />
          <div className="space-y-2">
            <LinkRow icon={Trophy} label="Achievements" sub={`${unlockedCount} unlocked`} onClick={() => navigate("/achievements")} />
            <LinkRow icon={Users} label="Group rides" onClick={() => navigate("/group-rides")} />
            <LinkRow icon={History} label="Ride history" onClick={() => navigate("/history")} />
            <LinkRow icon={ShieldAlert} label="Safety & SOS" onClick={() => navigate("/safety")} />
          </div>
        </div>

        <div>
          <SectionHeader title="Preferences" />
          <Card className="p-4 space-y-4">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Ruler size={15} className="text-[var(--color-ink-dim)]" />
                <span className="text-sm font-medium">Units</span>
              </div>
              <div className="flex gap-2">
                <Pill active={units === "metric"} onClick={() => updatePreferences({ units: "metric" })}>Metric</Pill>
                <Pill active={units === "imperial"} onClick={() => updatePreferences({ units: "imperial" })}>Imperial</Pill>
              </div>
            </div>

            <div className="pt-3 border-t border-[var(--color-border)]">
              <div className="flex items-center gap-2 mb-2">
                <RouteIcon size={15} className="text-[var(--color-ink-dim)]" />
                <span className="text-sm font-medium">Preferred route type</span>
              </div>
              <div className="flex gap-2 flex-wrap">
                {(["fastest", "curvy", "scenic", "offroad"] as const).map((t) => (
                  <Pill key={t} active={profile.preferences.routeType === t} onClick={() => updatePreferences({ routeType: t })}>
                    {t[0].toUpperCase() + t.slice(1)}
                  </Pill>
                ))}
              </div>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
              <span className="text-sm font-medium">Avoid highways</span>
              <Pill active={profile.preferences.avoidHighways} onClick={() => updatePreferences({ avoidHighways: !profile.preferences.avoidHighways })}>
                {profile.preferences.avoidHighways ? "On" : "Off"}
              </Pill>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

function StatChip({ value, label }: { value: string; label: string }) {
  return (
    <Card className="p-3 flex flex-col items-center text-center">
      <span className="font-display text-lg font-bold tabular-nums">{value}</span>
      <span className="text-[10px] text-[var(--color-ink-faint)]">{label}</span>
    </Card>
  );
}

function LinkRow({ icon: Icon, label, sub, onClick }: { icon: typeof Bike; label: string; sub?: string; onClick: () => void }) {
  return (
    <Card className="p-3.5 flex items-center gap-3" onClick={onClick}>
      <div className="w-9 h-9 rounded-full bg-[var(--color-surface-2)] flex items-center justify-center shrink-0">
        <Icon size={16} className="text-[var(--color-accent)]" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{label}</p>
        {sub && <p className="text-xs text-[var(--color-ink-faint)]">{sub}</p>}
      </div>
      <ChevronRight size={18} className="text-[var(--color-ink-faint)]" />
    </Card>
  );
}
