import { Route } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, Badge } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import { formatDistance, formatDuration, formatSpeed } from "../lib/geo";

export function RideHistoryScreen() {
  const rideHistory = useAppStore((s) => s.rideHistory);
  const units = useAppStore((s) => s.profile.preferences.units);

  return (
    <div>
      <TopBar title="Ride History" back />

      <div className="px-4 pt-4 space-y-3 pb-4">
        {rideHistory.map((r) => (
          <Card key={r.id} className="p-4">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <div className="w-9 h-9 rounded-full bg-[var(--color-accent-soft)] flex items-center justify-center">
                  <Route size={16} className="text-[var(--color-accent)]" />
                </div>
                <div>
                  <p className="text-sm font-semibold">{r.name}</p>
                  <p className="text-xs text-[var(--color-ink-faint)]">{r.date}</p>
                </div>
              </div>
              <Badge>{r.routeTag}</Badge>
            </div>
            <div className="grid grid-cols-3 gap-2 pt-2 border-t border-[var(--color-border)] text-center">
              <div>
                <p className="font-display font-bold tabular-nums">{formatDistance(r.distanceKm, units)}</p>
                <p className="text-[10px] text-[var(--color-ink-faint)]">Distance</p>
              </div>
              <div>
                <p className="font-display font-bold tabular-nums">{formatDuration(r.durationSec)}</p>
                <p className="text-[10px] text-[var(--color-ink-faint)]">Duration</p>
              </div>
              <div>
                <p className="font-display font-bold tabular-nums">{formatSpeed(r.maxSpeed, units)}</p>
                <p className="text-[10px] text-[var(--color-ink-faint)]">Top speed</p>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
