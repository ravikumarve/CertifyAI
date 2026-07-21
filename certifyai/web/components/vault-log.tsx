"use client";

import type { VaultEntry } from "@/lib/types";

interface VaultLogProps {
  entries: VaultEntry[];
}

export default function VaultLog({ entries }: VaultLogProps) {
  const logLines = entries.map((e) => {
    const time = e.timestamp ? formatTime(e.timestamp) : "—";
    let text = e.message || "Recorded.";
    if (e.hash) text = e.hash;
    return { time, text, level: e.level || "INFO" };
  });

  return (
    <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-void)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase">
        <span>Evidence Vault Log</span>
        <span style={{ color: "var(--acid-green)" }}>
          {entries.length > 0 ? `${entries.length} ENTRIES` : "EMPTY"}
        </span>
      </div>

      {/* Log entries */}
      <div
        className="p-4 font-[family-name:var(--font-mono)] text-[0.75rem] leading-relaxed flex flex-col gap-2 overflow-y-auto"
        style={{ maxHeight: 480 }}
      >
        {entries.length === 0 ? (
          <div className="text-[var(--text-faint)] italic flex items-center gap-2">
            <span>No vault entries yet.</span>
          </div>
        ) : (
          logLines.map((line, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-[var(--text-faint)] shrink-0">[{line.time}]</span>
              <span
                className={
                  line.level === "FAIL" || line.level === "ERROR"
                    ? "text-[var(--electric-red)]"
                    : line.level === "WARN"
                      ? "text-[#FF6600]"
                      : "text-[var(--text-main)]"
                }
                style={{
                  wordBreak: line.text.length > 48 ? "break-all" : "normal",
                  fontSize: line.text.length > 64 ? "0.7rem" : "0.75rem",
                }}
              >
                {line.text}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function formatTime(iso: string): string {
  try {
    const d = new Date(iso);
    if (isNaN(d.getTime())) return iso.slice(0, 19);
    return `${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
  } catch {
    return iso;
  }
}
