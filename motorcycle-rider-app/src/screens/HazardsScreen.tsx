import { useState } from "react";
import { TriangleAlert, Plus, ThumbsUp, X } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, Badge, PrimaryButton, Pill } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import type { HazardReport, HazardType } from "../types";

const HAZARD_TYPES: { key: HazardType; label: string }[] = [
  { key: "pothole", label: "Pothole" },
  { key: "gravel", label: "Gravel" },
  { key: "debris", label: "Debris" },
  { key: "accident", label: "Accident" },
  { key: "construction", label: "Construction" },
  { key: "ice", label: "Ice" },
  { key: "animals", label: "Animals" },
  { key: "sharp_curve", label: "Sharp curve" },
  { key: "police", label: "Police" },
  { key: "slippery_surface", label: "Slippery" },
];

const severityTone: Record<string, "danger" | "warn" | "default"> = {
  critical: "danger",
  high: "danger",
  medium: "warn",
  low: "default",
};

export function HazardsScreen() {
  const hazards = useAppStore((s) => s.hazards);
  const reportHazard = useAppStore((s) => s.reportHazard);
  const [showForm, setShowForm] = useState(false);

  const submit = (type: HazardType, description: string) => {
    const hazard: HazardReport = {
      id: `h-${Date.now()}`,
      type,
      severity: "medium",
      description,
      distanceKm: Math.round(Math.random() * 8 * 10) / 10,
      reportedAt: "Just now",
      verifiedCount: 0,
    };
    reportHazard(hazard);
    setShowForm(false);
  };

  return (
    <div>
      <TopBar
        title="Hazards"
        action={
          <button
            onClick={() => setShowForm((v) => !v)}
            className="w-9 h-9 rounded-full bg-[var(--color-accent)] text-[#160900] flex items-center justify-center"
            aria-label="Report hazard"
          >
            {showForm ? <X size={18} /> : <Plus size={18} />}
          </button>
        }
      />

      <div className="px-4 pt-4 space-y-3 pb-4">
        {showForm && <ReportForm onSubmit={submit} />}

        {hazards.map((h) => (
          <Card key={h.id} className="p-4 flex gap-3">
            <div className="w-10 h-10 rounded-full bg-[#ff4b4b1a] flex items-center justify-center shrink-0">
              <TriangleAlert size={18} className="text-[var(--color-danger)]" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-0.5">
                <p className="text-sm font-semibold capitalize">{h.type.replace("_", " ")}</p>
                <Badge tone={severityTone[h.severity]}>{h.severity}</Badge>
              </div>
              <p className="text-sm text-[var(--color-ink-dim)] mb-2">{h.description}</p>
              <div className="flex items-center justify-between text-xs text-[var(--color-ink-faint)]">
                <span>{h.distanceKm} km ahead · {h.reportedAt}</span>
                <span className="flex items-center gap-1 text-[var(--color-ink-dim)]">
                  <ThumbsUp size={12} /> {h.verifiedCount}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

function ReportForm({ onSubmit }: { onSubmit: (type: HazardType, description: string) => void }) {
  const [type, setType] = useState<HazardType>("pothole");
  const [description, setDescription] = useState("");

  return (
    <Card className="p-4 space-y-3">
      <p className="text-sm font-semibold">Report a hazard</p>
      <div className="flex flex-wrap gap-1.5">
        {HAZARD_TYPES.map((t) => (
          <Pill key={t.key} active={type === t.key} onClick={() => setType(t.key)}>
            {t.label}
          </Pill>
        ))}
      </div>
      <textarea
        placeholder="What did you see?"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        rows={2}
        className="w-full bg-[var(--color-surface-2)] rounded-lg px-3 py-2 text-sm outline-none resize-none"
      />
      <PrimaryButton className="w-full" disabled={!description} onClick={() => onSubmit(type, description)}>
        Submit report
      </PrimaryButton>
    </Card>
  );
}
