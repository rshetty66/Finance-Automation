import { useNavigate } from "react-router-dom";
import { ChevronLeft } from "lucide-react";
import type { ReactNode } from "react";

export function TopBar({ title, back, action }: { title: string; back?: boolean; action?: ReactNode }) {
  const navigate = useNavigate();
  return (
    <header className="sticky top-0 z-30 safe-top bg-[#08090bee] backdrop-blur-md border-b border-[var(--color-border)]">
      <div className="mx-auto max-w-md flex items-center justify-between px-4 h-14">
        <div className="flex items-center gap-2 min-w-0">
          {back && (
            <button
              onClick={() => navigate(-1)}
              className="-ml-1.5 p-1.5 rounded-full text-[var(--color-ink-dim)] active:bg-[var(--color-surface-2)]"
              aria-label="Back"
            >
              <ChevronLeft size={22} />
            </button>
          )}
          <h1 className="font-display text-xl font-bold uppercase tracking-wide truncate">{title}</h1>
        </div>
        {action}
      </div>
    </header>
  );
}
