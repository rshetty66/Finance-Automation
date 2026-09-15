import { Calendar, MapPin, Users, Crown, Shield } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, Badge, PrimaryButton } from "../components/ui";
import { useAppStore } from "../store/useAppStore";

export function GroupRidesScreen() {
  const groupRides = useAppStore((s) => s.groupRides);

  return (
    <div>
      <TopBar title="Group Rides" />

      <div className="px-4 pt-4 space-y-4 pb-4">
        <PrimaryButton className="w-full h-12">
          <Users size={16} /> Create a group ride
        </PrimaryButton>

        {groupRides.map((ride) => (
          <Card key={ride.id} className="p-4">
            <div className="flex items-start justify-between mb-3">
              <div>
                <h3 className="font-display font-bold text-lg">{ride.name}</h3>
                <div className="flex items-center gap-1.5 text-xs text-[var(--color-ink-faint)] mt-1">
                  <Calendar size={12} /> {ride.scheduledFor}
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[var(--color-ink-faint)] mt-0.5">
                  <MapPin size={12} /> {ride.meetPoint}
                </div>
              </div>
              <Badge tone={ride.status === "active" ? "safe" : "default"}>{ride.status}</Badge>
            </div>

            <div className="flex items-center -space-x-2 mb-3">
              {ride.members.map((m) => (
                <div
                  key={m.id}
                  title={m.name}
                  className="w-9 h-9 rounded-full bg-[var(--color-surface-2)] border-2 border-[var(--color-surface)] flex items-center justify-center text-base"
                >
                  {m.avatarEmoji}
                </div>
              ))}
              <span className="pl-4 text-xs text-[var(--color-ink-faint)]">{ride.members.length} riders</span>
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-[var(--color-border)]">
              <div className="flex items-center gap-3 text-xs text-[var(--color-ink-dim)]">
                <span className="flex items-center gap-1"><Crown size={12} className="text-[var(--color-warn)]" /> {ride.members.find((m) => m.role === "leader")?.name ?? "—"}</span>
                <span className="flex items-center gap-1"><Shield size={12} /> {ride.distanceKm} km</span>
              </div>
              <button className="text-xs font-semibold text-[var(--color-accent)]">View details</button>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
