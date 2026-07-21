"use client";

import type { VaultEntry } from "@/lib/types";

interface VaultLogProps {
  entries: VaultEntry[];
}

export default function VaultLog({ entries }: VaultLogProps) {
  const logLines = entries.map((e) => {
    // Parse the stored metadata for display
    let message = "Recorded.";
    if (e.message) message = e.message;
    if (e.hash) {
      return { time: e.timestamp, text: message, hash: e.hash, level: e.level };
    }
    return { time: e.timestamp, text: message, hash: undefined, level: e.level };
  });

  return (
    <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col">
      <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-void)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase">
        <span>Evidence Vault Log</span>
        <span style={{ color: "var(--acid-green)" }}>
          {entries.length > 0 ? `${entries.length} ENTRIES` : "EMPTY"}
        </span>
      </div>
      <div className="p-4 font-[family-name:var(--font-mono)] text-[0.75rem] text-[var(--text-muted)] flex flex-col gap-2 overflow-y-auto max-h-[400px]">
        {entries.length === 0 ? (
          <div className="text-[var(--text-faint)] italic">No vault entries yet.</div>
        ) : (
          logLines.map((line, i) => (
            <div key={i}>
              <div className="flex gap-2">
                <span className="text-[var(--text-faint)] shrink-0">[{line.time}]</span>
                {line.hash ? (
                  <span className="text-[var(--text-main)] break-all">{line.hash}</span>
                ) : (
                  <span style={{ color: line.level === "FAIL" ? "var(--electric-red)" : "var(--acid-green)" }}>
                    {line.text}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
