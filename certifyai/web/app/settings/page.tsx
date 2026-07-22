"use client";

import { useEffect, useState } from "react";

interface ConfigResponse {
  config: Record<string, Record<string, string>>;
  source: string;
}

export default function SettingsPage() {
  const [configResp, setConfigResp] = useState<ConfigResponse | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadConfig() {
      try {
        const res = await fetch("/api/dashboard?mode=config");
        if (res.ok) {
          const json = await res.json();
          if (!json.error) setConfigResp(json);
        }
      } catch {
        // best-effort
      } finally {
        setLoading(false);
      }
    }
    loadConfig();
  }, []);

  const config = configResp?.config ?? {};

  // Flatten nested config for display
  const allEntries: { section: string; key: string; value: string }[] = [];
  for (const [section, fields] of Object.entries(config)) {
    if (typeof fields === "object" && fields !== null) {
      for (const [key, value] of Object.entries(fields)) {
        const val = value != null ? String(value) : "—";
        allEntries.push({ section, key, value: val });
      }
    } else {
      const val = fields != null ? String(fields) : "—";
      allEntries.push({ section: "general", key: section, value: val });
    }
  }

  const sections = [...new Set(allEntries.map((e) => e.section))];

  return (
    <>
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Settings
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            Provider &amp; system configuration
          </div>
          {configResp?.source && configResp.source !== "none" && (
            <div className="flex gap-2 mt-2">
              <span className="text-[0.7rem] px-2 py-0.5 border border-[var(--border-hard)] uppercase font-[family-name:var(--font-mono)] text-[var(--text-faint)]">
                Source: {configResp.source}
              </span>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center text-[var(--text-muted)] font-[family-name:var(--font-mono)] py-16">
          <div className="flex flex-col items-center gap-3">
            <div className="w-6 h-6 border-2 border-[var(--border-hard)] border-t-[var(--acid-green)] rounded-full animate-spin" />
            <span className="text-[0.8rem]">Loading config...</span>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {sections.length === 0 ? (
            <>
              {/* Empty state — show skeleton */}
              <div className="brut-card col-span-2">
                <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                  No Configuration
                </div>
                <div className="text-[var(--text-faint)] text-[0.85rem] font-[family-name:var(--font-mono)]">
                  No configuration found. Run an attack or create a config file to populate settings.
                </div>
              </div>
            </>
          ) : (
            sections.map((section) => {
              const entries = allEntries.filter((e) => e.section === section);
              return (
                <div key={section} className="brut-card">
                  <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
                    {section.replace(/_/g, " ")}
                  </div>
                  <div className="space-y-3">
                    {entries.map((entry) => (
                      <ConfigField
                        key={entry.key}
                        label={entry.key.replace(/_/g, " ")}
                        value={entry.key.toLowerCase().includes("key") || entry.key.toLowerCase().includes("secret") ? "••••••••" : entry.value}
                      />
                    ))}
                  </div>
                </div>
              );
            })
          )}

          {/* Engine Info — always visible */}
          <div className="brut-card">
            <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-6">
              Engine
            </div>
            <div className="space-y-3">
              <ConfigField
                label="Engine Status"
                value="ONLINE"
                valueColor="var(--acid-green)"
              />
              <ConfigField label="Version" value="v1.0.4" />
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function ConfigField({
  label,
  value,
  valueColor,
}: {
  label: string;
  value: string;
  valueColor?: string;
}) {
  return (
    <div className="flex justify-between items-center">
      <span className="text-[var(--text-muted)] text-[0.8rem] font-[family-name:var(--font-mono)] uppercase">
        {label}
      </span>
      <span
        className="text-[var(--text-main)] text-[0.9rem] font-[family-name:var(--font-mono)]"
        style={valueColor ? { color: valueColor } : undefined}
      >
        {value}
      </span>
    </div>
  );
}
