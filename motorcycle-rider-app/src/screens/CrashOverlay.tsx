import { useEffect } from "react";
import { Siren, CheckCircle2 } from "lucide-react";
import { useAppStore } from "../store/useAppStore";
import { PrimaryButton } from "../components/ui";

export function CrashOverlay() {
  const crashEvent = useAppStore((s) => s.crashEvent);
  const countdownActive = useAppStore((s) => s.countdownActive);
  const countdownSeconds = useAppStore((s) => s.countdownSeconds);
  const cancelCrash = useAppStore((s) => s.cancelCrash);
  const confirmSos = useAppStore((s) => s.confirmSos);
  const tickCountdown = useAppStore((s) => s.tickCountdown);

  useEffect(() => {
    if (!countdownActive) return;
    const id = setInterval(() => tickCountdown(), 1000);
    return () => clearInterval(id);
  }, [countdownActive, tickCountdown]);

  if (!crashEvent) return null;
  if (crashEvent.status === "false_alarm") return null;

  const sosSent = crashEvent.status === "confirmed" && !countdownActive;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-end sm:items-center justify-center p-4">
      <div className="w-full max-w-md rounded-3xl bg-[var(--color-surface)] border border-[var(--color-danger)] p-6 text-center">
        {!sosSent ? (
          <>
            <div className="w-16 h-16 mx-auto rounded-full bg-[#ff4b4b22] flex items-center justify-center mb-4 relative text-[var(--color-danger)]">
              <span className="pulse-ring absolute inset-0 text-[var(--color-danger)] opacity-40" />
              <Siren size={30} className="relative" />
            </div>
            <h2 className="font-display text-2xl font-bold text-[var(--color-danger)] mb-1">Crash Detected</h2>
            <p className="text-sm text-[var(--color-ink-dim)] mb-1">
              {crashEvent.severity[0].toUpperCase() + crashEvent.severity.slice(1)} severity impact ({crashEvent.impactForce.toFixed(1)}G)
            </p>
            <p className="text-xs text-[var(--color-ink-faint)] mb-5">
              Sending SOS to your emergency contacts automatically.
            </p>
            <div className="font-display text-6xl font-extrabold tabular-nums mb-5">{countdownSeconds}</div>
            <div className="flex flex-col gap-2">
              <PrimaryButton tone="safe" className="w-full h-14" onClick={cancelCrash}>
                I'm OK — Cancel
              </PrimaryButton>
              <PrimaryButton tone="danger" className="w-full h-12" onClick={confirmSos}>
                Send SOS Now
              </PrimaryButton>
            </div>
          </>
        ) : (
          <>
            <div className="w-16 h-16 mx-auto rounded-full bg-[#33d17a22] flex items-center justify-center mb-4 text-[var(--color-safe)]">
              <CheckCircle2 size={30} />
            </div>
            <h2 className="font-display text-2xl font-bold mb-1">SOS Sent</h2>
            <p className="text-sm text-[var(--color-ink-dim)] mb-6">
              Your emergency contacts have been notified with your location. Help is on the way.
            </p>
            <PrimaryButton tone="neutral" className="w-full h-12" onClick={cancelCrash}>
              Close
            </PrimaryButton>
          </>
        )}
      </div>
    </div>
  );
}
