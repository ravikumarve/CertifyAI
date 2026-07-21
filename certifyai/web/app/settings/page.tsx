"use client";

import { useEffect, useState } from "react";

interface Config {
  provider?: { name?: string; model?: string; api_key?: string };
  paths?: { vault?: string; database?: string };
  frameworks?: string[];
  attack_categories?: string | null;
}

export default function SettingsPage() {
  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Load config from API
    async function loadConfig() {
      try {
        const res = await fetch("/api/dashboard?mode=config");
        if (res.ok) {
          const json = await res.json();
          if (!json.error) setConfig(json.config ?? json);
        }
      } catch {
        // Silently fail — config loading is best-effort
      } finally {
        setLoading(false);
      }
    }
    loadConfig();
  }, []);

  return (
    <>
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Settings
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            Provider & system configuration
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center text-[var(--text-muted)] font-[family-name:var(--font-mono)]">
          Loading config...
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {/* Provider Config */}
          <div className="brut-card">
            <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
              Provider Configuration
            </div>
            <div className="space-y-4">
              <ConfigField label="Provider" value={config?.provider?.name ?? "—"} />
              <ConfigField label="Model" value={config?.provider?.model ?? "—"} />
              <ConfigField
                label="API Key"
                value={config?.provider?.api_key ? "••••••••" : "—"}
              />
            </div>
          </div>

          {/* Paths Config */}
          <div className="brut-card">
            <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
              Paths
            </div>
            <div className="space-y-4">
              <ConfigField label="Vault Directory" value={config?.paths?.vault ?? "—"} />
              <ConfigField label="Database Path" value={config?.paths?.database ?? "—"} />
            </div>
          </div>

          {/* Frameworks */}
          <div className="brut-card">
            <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
              Compliance Frameworks
            </div>
            <div className="flex flex-wrap gap-2">
              {(config?.frameworks ?? []).length > 0
                ? config!.frameworks!.map((fw) => (
                    <span
                      key={fw}
                      className="px-3 py-1 border border-[var(--border-hard)] text-[0.75rem] font-[family-name:var(--font-mono)] uppercase"
                    >
                      {fw}
                    </span>
                  ))
                : <span className="text-[var(--text-muted)] text-[0.8rem]">No frameworks configured</span>
              }
            </div>
          </div>

          {/* Engine Info */}
          <div className="brut-card">
            <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
              Engine
            </div>
            <div className="space-y-4">
              <ConfigField label="Engine Status" value="ONLINE" valueColor="var(--acid-green)" />
              <ConfigField label="Version" value="v1.0.4" />
              <ConfigField label="Attack Categories" value={config?.attack_categories ?? "All"} />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function ConfigField({ label, value, valueColor }: { label: string; value: string; valueColor?: string }) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-[var(--text-muted)] text-[0.8rem] font-[family-name:var(--font-mono)] uppercase">{label}</span>
      <span
        className="text-[var(--text-main)] text-[0.9rem] font-[family-name:var(--font-mono)]"
        style={valueColor ? { color: valueColor } : undefined}
      >
        {value}
      </span>
    </div>
  );
}
