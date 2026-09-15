import type { PropsWithChildren, ReactNode } from "react";

export function Card({
  children,
  className = "",
  onClick,
}: PropsWithChildren<{ className?: string; onClick?: () => void }>) {
  return (
    <div
      onClick={onClick}
      className={`rounded-2xl border border-[var(--color-border)] bg-[var(--color-surface)] ${onClick ? "cursor-pointer active:scale-[0.99] transition-transform" : ""} ${className}`}
    >
      {children}
    </div>
  );
}

export function SectionHeader({
  title,
  action,
}: {
  title: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex items-center justify-between mb-3">
      <h2 className="font-display text-lg font-semibold uppercase tracking-wide text-[var(--color-ink)]">{title}</h2>
      {action}
    </div>
  );
}

export function StatTile({
  label,
  value,
  unit,
  icon,
}: {
  label: string;
  value: string | number;
  unit?: string;
  icon?: ReactNode;
}) {
  return (
    <Card className="p-3 flex flex-col gap-1">
      <div className="flex items-center gap-1.5 text-[var(--color-ink-faint)]">
        {icon}
        <span className="text-[11px] uppercase tracking-wide font-medium">{label}</span>
      </div>
      <div className="flex items-baseline gap-1">
        <span className="font-display text-2xl font-bold text-[var(--color-ink)] tabular-nums">{value}</span>
        {unit && <span className="text-xs text-[var(--color-ink-dim)]">{unit}</span>}
      </div>
    </Card>
  );
}

export function ScoreBar({ label, score, color }: { label: string; score: number; color: string }) {
  return (
    <div className="flex-1 min-w-[70px]">
      <div className="flex items-center justify-between mb-1">
        <span className="text-[10px] uppercase tracking-wide text-[var(--color-ink-faint)]">{label}</span>
        <span className="text-[10px] font-semibold tabular-nums" style={{ color }}>
          {Math.round(score)}
        </span>
      </div>
      <div className="h-1.5 rounded-full bg-[var(--color-surface-2)] overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{ width: `${Math.min(100, score)}%`, backgroundColor: color }}
        />
      </div>
    </div>
  );
}

export function Pill({
  children,
  active,
  onClick,
  tone = "default",
}: PropsWithChildren<{ active?: boolean; onClick?: () => void; tone?: "default" | "danger" | "safe" }>) {
  const toneColor =
    tone === "danger" ? "var(--color-danger)" : tone === "safe" ? "var(--color-safe)" : "var(--color-accent)";
  return (
    <button
      onClick={onClick}
      className="px-3 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition-colors"
      style={
        active
          ? { backgroundColor: toneColor, color: "#0A0A0A" }
          : { backgroundColor: "var(--color-surface-2)", color: "var(--color-ink-dim)" }
      }
    >
      {children}
    </button>
  );
}

export function Badge({ tone = "default", children }: PropsWithChildren<{ tone?: "default" | "danger" | "safe" | "warn" }>) {
  const map: Record<string, string> = {
    default: "bg-[var(--color-accent-soft)] text-[var(--color-accent)]",
    danger: "bg-[#ff4b4b22] text-[var(--color-danger)]",
    safe: "bg-[#33d17a22] text-[var(--color-safe)]",
    warn: "bg-[#ffb54522] text-[var(--color-warn)]",
  };
  return <span className={`px-2 py-0.5 rounded-md text-[11px] font-semibold ${map[tone]}`}>{children}</span>;
}

export function PrimaryButton({
  children,
  onClick,
  tone = "accent",
  className = "",
  disabled,
}: PropsWithChildren<{ onClick?: () => void; tone?: "accent" | "danger" | "safe" | "neutral"; className?: string; disabled?: boolean }>) {
  const toneMap: Record<string, string> = {
    accent: "bg-[var(--color-accent)] text-[#160900]",
    danger: "bg-[var(--color-danger)] text-[#1a0505]",
    safe: "bg-[var(--color-safe)] text-[#04160c]",
    neutral: "bg-[var(--color-surface-2)] text-[var(--color-ink)]",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`flex items-center justify-center gap-2 rounded-xl font-display font-bold uppercase tracking-wide text-sm py-3 px-4 transition-transform active:scale-[0.98] disabled:opacity-40 ${toneMap[tone]} ${className}`}
    >
      {children}
    </button>
  );
}
