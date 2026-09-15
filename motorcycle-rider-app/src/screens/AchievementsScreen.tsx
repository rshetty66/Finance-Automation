import { TopBar } from "../components/TopBar";
import { Card } from "../components/ui";
import { useAppStore } from "../store/useAppStore";

const tierColor: Record<string, string> = {
  bronze: "#c98a4b",
  silver: "#c2c6cc",
  gold: "#ffcf4d",
  platinum: "#8fd8ff",
};

export function AchievementsScreen() {
  const achievements = useAppStore((s) => s.achievements);
  const unlocked = achievements.filter((a) => a.unlockedAt);

  return (
    <div>
      <TopBar title="Achievements" />

      <div className="px-4 pt-4 pb-4">
        <Card className="p-4 mb-4 text-center">
          <p className="font-display text-4xl font-bold text-[var(--color-accent)]">{unlocked.length}<span className="text-lg text-[var(--color-ink-faint)]">/{achievements.length}</span></p>
          <p className="text-xs text-[var(--color-ink-faint)] mt-1">Badges unlocked</p>
        </Card>

        <div className="grid grid-cols-2 gap-3">
          {achievements.map((a) => {
            const done = !!a.unlockedAt;
            const pct = Math.min(100, (a.progress / a.target) * 100);
            return (
              <Card key={a.id} className={`p-4 flex flex-col items-center text-center gap-1.5 ${done ? "" : "opacity-70"}`}>
                <div
                  className="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl mb-1"
                  style={{ backgroundColor: `${tierColor[a.tier]}22`, filter: done ? "none" : "grayscale(0.6)" }}
                >
                  {a.icon}
                </div>
                <p className="text-sm font-semibold leading-tight">{a.name}</p>
                <p className="text-[11px] text-[var(--color-ink-faint)] leading-snug">{a.description}</p>
                <div className="w-full h-1.5 rounded-full bg-[var(--color-surface-2)] mt-1 overflow-hidden">
                  <div className="h-full rounded-full" style={{ width: `${pct}%`, backgroundColor: tierColor[a.tier] }} />
                </div>
                <span className="text-[10px] text-[var(--color-ink-faint)] uppercase tracking-wide font-semibold" style={{ color: tierColor[a.tier] }}>
                  {a.tier}
                </span>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
