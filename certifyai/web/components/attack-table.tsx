"use client";

import type { AttackResult } from "@/lib/types";

interface AttackTableProps {
  results: AttackResult[];
  frameworks?: string[];
  concurrency?: number;
  isRunning?: boolean;
  completedCount?: number;
  totalCount?: number;
}

function statusClass(status: string): string {
  switch (status.toLowerCase()) {
    case "pass": return "status-pass";
    case "fail": return "status-fail";
    case "running": return "status-run";
    default: return "";
  }
}

export default function AttackTable({ results, frameworks, concurrency, isRunning, completedCount, totalCount }: AttackTableProps) {
  return (
    <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col">
      <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-panel)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase">
        <span>Live Attack Stream</span>
        <span style={{ color: "var(--cyber-blue)" }}>
          {isRunning ? `EXECUTING (${completedCount}/${totalCount})` : "COMPLETED"}
        </span>
      </div>

      {(frameworks || concurrency) && (
        <div className="flex gap-8 px-4 py-3 border-b border-[var(--border-hard)] font-[family-name:var(--font-mono)] text-[0.8rem]">
          {frameworks && (
            <div className="flex flex-col gap-1">
              <span className="text-[0.7rem] text-[var(--text-muted)] uppercase">Frameworks</span>
              <span style={{ color: "var(--cyber-blue)" }} className="font-bold">
                {frameworks.join(", ")}
              </span>
            </div>
          )}
          {concurrency && (
            <div className="flex flex-col gap-1">
              <span className="text-[0.7rem] text-[var(--text-muted)] uppercase">Concurrency</span>
              <span style={{ color: "var(--cyber-blue)" }} className="font-bold">
                {concurrency} Threads
              </span>
            </div>
          )}
        </div>
      )}

      <table className="brut-table">
        <thead>
          <tr>
            <th>Scenario</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {results.length === 0 ? (
            <tr>
              <td colSpan={4} className="text-[var(--text-muted)] text-center py-8">
                No results yet. Run an attack from the CLI or TUI.
              </td>
            </tr>
          ) : (
            results.map((r) => (
              <tr key={r.id}>
                <td>{r.scenario_id}</td>
                <td>{r.category}</td>
                <td className="uppercase font-bold text-[0.7rem]" style={{ color: severityColor(r.severity) }}>
                  {r.severity}
                </td>
                <td className={statusClass(r.status)}>{r.status}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function severityColor(sev: string): string {
  switch (sev.toLowerCase()) {
    case "critical": return "var(--electric-red)";
    case "high": return "#FF6600";
    case "medium": return "var(--cyber-blue)";
    case "low": return "var(--text-muted)";
    default: return "var(--text-main)";
  }
}
