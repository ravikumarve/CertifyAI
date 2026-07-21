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
    case "pass":
      return "status-pass";
    case "fail":
      return "status-fail";
    case "running":
      return "status-run";
    default:
      return "";
  }
}

function severityColor(sev: string): string {
  switch (sev.toLowerCase()) {
    case "critical":
      return "var(--electric-red)";
    case "high":
      return "#FF6600";
    case "medium":
      return "var(--cyber-blue)";
    case "low":
      return "var(--text-muted)";
    default:
      return "var(--text-main)";
  }
}

export default function AttackTable({
  results,
  frameworks,
  concurrency,
  isRunning,
  completedCount,
  totalCount,
}: AttackTableProps) {
  return (
    <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-panel)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase">
        <span>Live Attack Stream</span>
        <span style={{ color: "var(--cyber-blue)" }}>
          {isRunning
            ? `EXECUTING (${completedCount ?? 0}/${totalCount ?? "?"})`
            : results.length > 0
              ? "COMPLETED"
              : "READY"}
        </span>
      </div>

      {/* Config bar */}
      {(frameworks && frameworks.length > 0) || concurrency ? (
        <div className="flex gap-8 px-4 py-3 border-b border-[var(--border-hard)] font-[family-name:var(--font-mono)] text-[0.8rem]">
          {frameworks && frameworks.length > 0 && (
            <div className="flex flex-col gap-1">
              <span className="text-[0.7rem] text-[var(--text-muted)] uppercase">
                Frameworks
              </span>
              <span className="font-bold" style={{ color: "var(--cyber-blue)" }}>
                {frameworks.join(", ")}
              </span>
            </div>
          )}
          {concurrency && (
            <div className="flex flex-col gap-1">
              <span className="text-[0.7rem] text-[var(--text-muted)] uppercase">
                Concurrency
              </span>
              <span className="font-bold" style={{ color: "var(--cyber-blue)" }}>
                {concurrency} Threads
              </span>
            </div>
          )}
        </div>
      ) : null}

      {/* Table */}
      <table className="brut-table">
        <thead>
          <tr>
            <th>Scenario</th>
            <th>Category</th>
            <th>Severity</th>
            <th>Status</th>
            <th>Response</th>
          </tr>
        </thead>
        <tbody>
          {results.length === 0 ? (
            <tr>
              <td colSpan={5} className="text-[var(--text-muted)] text-center py-8">
                {isRunning ? (
                  <span className="flex items-center justify-center gap-2">
                    <span className="w-4 h-4 border-2 border-[var(--border-hard)] border-t-[var(--cyber-blue)] rounded-full animate-spin" />
                    Waiting for results...
                  </span>
                ) : (
                  <span>
                    No results yet. Run an attack from the{" "}
                    <code className="text-[var(--cyber-blue)]">CLI</code> or{" "}
                    <code className="text-[var(--cyber-blue)]">TUI</code>.
                  </span>
                )}
              </td>
            </tr>
          ) : (
            results.map((r) => (
              <tr key={r.id}>
                <td>{r.scenario_id}</td>
                <td>{r.category}</td>
                <td
                  className="uppercase font-bold text-[0.7rem]"
                  style={{ color: severityColor(r.severity) }}
                >
                  {r.severity}
                </td>
                <td>
                  <span className={statusClass(r.status)}>{r.status}</span>
                </td>
                <td className="text-[var(--text-faint)] text-[0.75rem] font-[family-name:var(--font-mono)]">
                  {r.response_time_ms != null ? `${r.response_time_ms}ms` : "—"}
                </td>
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
