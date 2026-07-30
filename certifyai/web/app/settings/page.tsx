"use client";

import { useCallback, useEffect, useState } from "react";

interface SettingsConfig {
  provider: { name: string; model: string; api_key: string };
  paths: { vault: string; database: string; concurrency: string };
  frameworks: string[];
  reports: { output: string };
}

const DEFAULT_CONFIG: SettingsConfig = {
  provider: { name: "openai", model: "gpt-4o", api_key: "" },
  paths: { vault: "./certifyai_vault", database: "certifyai.db", concurrency: "3" },
  frameworks: ["eu_ai_act", "soc2", "nist_ai_rmf"],
  reports: { output: "./reports/compliance.json" },
};

const FRAMEWORK_OPTIONS = [
  { label: "All Frameworks", value: "all" },
  { label: "EU AI Act", value: "eu_ai_act" },
  { label: "SOC 2 Type II", value: "soc2" },
  { label: "NIST AI RMF", value: "nist_ai_rmf" },
];

export default function SettingsPage() {
  const [config, setConfig] = useState<SettingsConfig>(DEFAULT_CONFIG);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMsg, setStatusMsg] = useState<{ text: string; ok: boolean } | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await fetch("/api/settings");
        if (res.ok) {
          const data = await res.json();
          if (!data.error) {
            setConfig({
              provider: { name: data.provider?.name ?? "", model: data.provider?.model ?? "", api_key: data.provider?.api_key ?? "" },
              paths: { vault: data.paths?.vault ?? "", database: data.paths?.database ?? "", concurrency: data.paths?.concurrency ?? "3" },
              frameworks: data.frameworks ?? [],
              reports: { output: data.reports?.output ?? "" },
            });
          }
        }
      } catch {
        // best-effort
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const handleChange = useCallback(
    (section: string, field: string, value: string) => {
      setConfig((prev) => {
        const next = { ...prev };
        if (section === "frameworks") {
          next.frameworks = value === "all" ? ["eu_ai_act", "soc2", "nist_ai_rmf"] : [value];
        } else if (section === "reports") {
          next.reports = { ...next.reports, [field]: value };
        } else if (section in next) {
          const sec = next[section as keyof SettingsConfig];
          if (typeof sec === "object" && sec !== null && !Array.isArray(sec)) {
            (sec as Record<string, string>)[field] = value;
          }
        }
        return next;
      });
      setStatusMsg(null);
    },
    []
  );

  const handleSave = useCallback(async () => {
    setSaving(true);
    setStatusMsg(null);
    try {
      const res = await fetch("/api/settings", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      if (data.error) {
        setStatusMsg({ text: `Save failed: ${data.error}`, ok: false });
      } else {
        setStatusMsg({ text: "Configuration saved successfully", ok: true });
      }
    } catch (err) {
      setStatusMsg({ text: `Save failed: ${err}`, ok: false });
    } finally {
      setSaving(false);
    }
  }, [config]);

  const frameworkVal =
    config.frameworks.length === 1 ? config.frameworks[0] : "all";

  if (loading) {
    return (
      <div className="flex items-center justify-center text-[var(--text-muted)] font-[family-name:var(--font-mono)] py-16">
        <div className="flex flex-col items-center gap-3">
          <div className="w-6 h-6 border-2 border-[var(--border-hard)] border-t-[var(--acid-green)] rounded-full animate-spin" />
          <span className="text-[0.8rem]">Loading settings...</span>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* ── Top Bar ── */}
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Settings
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            Provider &amp; compliance configuration
          </div>
        </div>
        <div className="flex items-center gap-3">
          {statusMsg && (
            <span
              className={`text-[0.75rem] font-[family-name:var(--font-mono)] ${
                statusMsg.ok ? "text-[var(--acid-green)]" : "text-[var(--electric-red)]"
              }`}
            >
              {statusMsg.text}
            </span>
          )}
          <button
            onClick={handleSave}
            disabled={saving}
            className="brut-btn brut-btn-primary flex items-center gap-2"
          >
            {saving && (
              <div className="w-3.5 h-3.5 border-2 border-[var(--bg-void)] border-t-transparent rounded-full animate-spin" />
            )}
            {saving ? "Saving..." : "Save Configuration"}
          </button>
        </div>
      </div>

      {/* ── Settings Grid ── */}
      <div className="settings-grid">
        {/* ── Panel: Provider Configuration ── */}
        <div className="settings-panel">
          <div className="sp-title">Provider Configuration</div>
          <div className="field-group">
            <div className="field-label">Provider (openai / anthropic / ollama)</div>
            <input
              className="field-input"
              type="text"
              value={config.provider.name}
              onChange={(e) => handleChange("provider", "name", e.target.value)}
            />
          </div>
          <div className="field-group">
            <div className="field-label">Model (e.g. gpt-4o, claude-4, llama3.1)</div>
            <input
              className="field-input"
              type="text"
              value={config.provider.model}
              onChange={(e) => handleChange("provider", "model", e.target.value)}
            />
          </div>
          <div className="field-group">
            <div className="field-label">API Key</div>
            <input
              className="field-input"
              type="password"
              value={config.provider.api_key}
              onChange={(e) => handleChange("provider", "api_key", e.target.value)}
            />
          </div>
        </div>

        {/* ── Panel: Paths ── */}
        <div className="settings-panel">
          <div className="sp-title">Paths</div>
          <div className="field-group">
            <div className="field-label">Vault Directory</div>
            <input
              className="field-input"
              type="text"
              value={config.paths.vault}
              onChange={(e) => handleChange("paths", "vault", e.target.value)}
            />
          </div>
          <div className="field-group">
            <div className="field-label">Database Path</div>
            <input
              className="field-input"
              type="text"
              value={config.paths.database}
              onChange={(e) => handleChange("paths", "database", e.target.value)}
            />
          </div>
          <div className="field-group">
            <div className="field-label">Concurrency</div>
            <input
              className="field-input"
              type="text"
              value={config.paths.concurrency}
              onChange={(e) => handleChange("paths", "concurrency", e.target.value)}
            />
          </div>
        </div>

        {/* ── Panel: Compliance Framework (full width) ── */}
        <div className="settings-panel full">
          <div className="sp-title">Compliance Framework</div>
          <div className="field-row-2">
            <div className="field-group">
              <div className="field-label">Active Framework</div>
              <select
                className="field-select"
                value={frameworkVal}
                onChange={(e) => handleChange("frameworks", "", e.target.value)}
              >
                {FRAMEWORK_OPTIONS.map((opt) => (
                  <option key={opt.value} value={opt.value}>
                    {opt.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="field-group">
              <div className="field-label">Report Output Path</div>
              <input
                className="field-input"
                type="text"
                value={config.reports.output}
                onChange={(e) => handleChange("reports", "output", e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
