import { NavLink } from "react-router-dom";
import { Gauge, Navigation2, MapPinned, ShieldAlert, UserRound } from "lucide-react";

const TABS = [
  { to: "/", label: "Home", icon: Gauge, end: true },
  { to: "/ride", label: "Ride", icon: Navigation2 },
  { to: "/routes", label: "Routes", icon: MapPinned },
  { to: "/safety", label: "Safety", icon: ShieldAlert },
  { to: "/profile", label: "Profile", icon: UserRound },
];

export function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 border-t border-[var(--color-border)] bg-[#0a0a0bee] backdrop-blur-md safe-bottom">
      <div className="mx-auto max-w-md grid grid-cols-5">
        {TABS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex flex-col items-center justify-center gap-1 py-2.5 transition-colors ${
                isActive ? "text-[var(--color-accent)]" : "text-[var(--color-ink-faint)]"
              }`
            }
          >
            {({ isActive }) => (
              <>
                <Icon size={22} strokeWidth={isActive ? 2.4 : 1.8} />
                <span className="text-[10px] font-semibold uppercase tracking-wide">{label}</span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
