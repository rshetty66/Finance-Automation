import { useState } from "react";
import { ShieldCheck, Siren, Phone, Plus, Trash2, ChevronRight } from "lucide-react";
import { TopBar } from "../components/TopBar";
import { Card, SectionHeader, PrimaryButton, Pill } from "../components/ui";
import { useAppStore } from "../store/useAppStore";
import type { SafetyContact } from "../types";

export function SafetyScreen() {
  const profile = useAppStore((s) => s.profile);
  const updatePreferences = useAppStore((s) => s.updatePreferences);
  const updateProfile = useAppStore((s) => s.updateProfile);
  const triggerCrash = useAppStore((s) => s.triggerCrash);
  const [showAddContact, setShowAddContact] = useState(false);

  const removeContact = (id: string) => {
    updateProfile({ safetyContacts: profile.safetyContacts.filter((c) => c.id !== id) });
  };

  const addContact = (contact: SafetyContact) => {
    updateProfile({ safetyContacts: [...profile.safetyContacts, contact] });
    setShowAddContact(false);
  };

  const simulateCrash = () => {
    triggerCrash({
      id: `crash-${Date.now()}`,
      timestamp: new Date().toISOString(),
      severity: "moderate",
      impactForce: 6.2,
      status: "countdown",
    });
  };

  return (
    <div>
      <TopBar title="Safety" />

      <div className="px-4 pt-4 space-y-5 pb-4">
        <Card className="p-4 flex items-center gap-3 border-[var(--color-safe)]">
          <div className="w-11 h-11 rounded-full bg-[#33d17a22] flex items-center justify-center shrink-0">
            <ShieldCheck size={22} className="text-[var(--color-safe)]" />
          </div>
          <div className="flex-1">
            <p className="font-semibold text-sm">Crash detection {profile.preferences.crashDetectionEnabled ? "active" : "off"}</p>
            <p className="text-xs text-[var(--color-ink-faint)]">Monitoring motion sensors for impact events</p>
          </div>
          <Toggle
            checked={profile.preferences.crashDetectionEnabled}
            onChange={(v) => updatePreferences({ crashDetectionEnabled: v })}
          />
        </Card>

        <div>
          <SectionHeader title="Sensitivity" />
          <div className="flex gap-2">
            {(["low", "medium", "high"] as const).map((level) => (
              <Pill
                key={level}
                active={profile.preferences.crashDetectionSensitivity === level}
                onClick={() => updatePreferences({ crashDetectionSensitivity: level })}
              >
                {level[0].toUpperCase() + level.slice(1)}
              </Pill>
            ))}
          </div>
          <p className="text-xs text-[var(--color-ink-faint)] mt-2">
            Higher sensitivity reacts faster but may trigger more false alarms on rough roads.
          </p>
        </div>

        <PrimaryButton tone="danger" className="w-full h-16 text-base" onClick={simulateCrash}>
          <Siren size={20} /> Manual SOS
        </PrimaryButton>
        <button onClick={simulateCrash} className="block w-full text-center text-xs text-[var(--color-ink-faint)] -mt-3">
          Simulate a crash detection (demo)
        </button>

        <div>
          <SectionHeader
            title="Emergency contacts"
            action={
              <button
                onClick={() => setShowAddContact((v) => !v)}
                className="text-xs font-semibold text-[var(--color-accent)] flex items-center gap-0.5"
              >
                <Plus size={14} /> Add
              </button>
            }
          />
          <div className="space-y-2">
            {profile.safetyContacts.map((c) => (
              <Card key={c.id} className="p-3 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-[var(--color-surface-2)] flex items-center justify-center shrink-0">
                  <Phone size={15} className="text-[var(--color-ink-dim)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{c.name}</p>
                  <p className="text-xs text-[var(--color-ink-faint)]">{c.phone} · {c.relationship}</p>
                </div>
                <button onClick={() => removeContact(c.id)} className="p-1.5 text-[var(--color-ink-faint)]" aria-label="Remove">
                  <Trash2 size={15} />
                </button>
              </Card>
            ))}
          </div>
          {showAddContact && <AddContactForm onAdd={addContact} onCancel={() => setShowAddContact(false)} />}
        </div>

        <Card className="p-4 flex items-center gap-3">
          <div className="flex-1">
            <p className="text-sm font-medium">SOS countdown</p>
            <p className="text-xs text-[var(--color-ink-faint)]">Time before auto-alert sends</p>
          </div>
          <span className="font-display text-2xl font-bold text-[var(--color-accent)] tabular-nums">
            {profile.preferences.sosCountdownSeconds}s
          </span>
        </Card>
        <input
          type="range"
          min={10}
          max={60}
          step={5}
          value={profile.preferences.sosCountdownSeconds}
          onChange={(e) => updatePreferences({ sosCountdownSeconds: Number(e.target.value) })}
          className="w-full accent-[var(--color-accent)]"
        />

        <Card className="p-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-medium">Hazard alerts</p>
            <p className="text-xs text-[var(--color-ink-faint)]">Get notified of nearby road hazards</p>
          </div>
          <ChevronRight size={18} className="text-[var(--color-ink-faint)]" />
        </Card>
      </div>
    </div>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className="w-12 h-7 rounded-full relative transition-colors shrink-0"
      style={{ backgroundColor: checked ? "var(--color-safe)" : "var(--color-surface-2)" }}
    >
      <span
        className="absolute top-1 w-5 h-5 rounded-full bg-white transition-transform"
        style={{ transform: checked ? "translateX(22px)" : "translateX(4px)" }}
      />
    </button>
  );
}

function AddContactForm({ onAdd, onCancel }: { onAdd: (c: SafetyContact) => void; onCancel: () => void }) {
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [relationship, setRelationship] = useState("");

  return (
    <Card className="p-3 mt-2 space-y-2">
      <input
        placeholder="Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        className="w-full bg-[var(--color-surface-2)] rounded-lg px-3 py-2 text-sm outline-none"
      />
      <input
        placeholder="Phone number"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        className="w-full bg-[var(--color-surface-2)] rounded-lg px-3 py-2 text-sm outline-none"
      />
      <input
        placeholder="Relationship"
        value={relationship}
        onChange={(e) => setRelationship(e.target.value)}
        className="w-full bg-[var(--color-surface-2)] rounded-lg px-3 py-2 text-sm outline-none"
      />
      <div className="flex gap-2 pt-1">
        <PrimaryButton tone="neutral" className="flex-1" onClick={onCancel}>Cancel</PrimaryButton>
        <PrimaryButton
          className="flex-1"
          disabled={!name || !phone}
          onClick={() =>
            onAdd({
              id: `c-${Date.now()}`,
              name,
              phone,
              relationship: relationship || "Contact",
              notifyOnCrash: true,
              notifyOnRideStart: false,
            })
          }
        >
          Save
        </PrimaryButton>
      </div>
    </Card>
  );
}
