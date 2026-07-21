"use client";

import { useEffect, useState } from "react";
import type { RunSummary } from "@/lib/types";

export default function ResultsPage() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchRuns() {
      try {
        const res = await fetch("/api/dashboard?mode=runs");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (json.error) throw new Error(json.error);
        setRuns(json.runs ?? []);
      } catch (err) {
        setError(String(err));
      } finally {
        setLoading(false);
      }
    }
    fetchRuns();
  }, []);

  return (
    <>
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Results History
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            All attack runs
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-[var(--text-muted)] font-[family-name:var(--font-mono)]">
          Loading results...
        </div>
      ) : (
        <div className="bg-[var(--bg-void)] border border-[var(--border-hard)]">
          <table className="brut-table">
            <thead>
              <tr>
                <th>Run ID</th>
                <th>Provider</th>
                <th>Model</th>
                <th>Status</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Score</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="text-[var(--text-muted)] text-center py-8">
                    No runs yet.
                  </td>
                </tr>
              ) : (
                runs.map((run) => (
                  <tr key={run.id}>
                    <td className="font-[family-name:var(--font-mono)] text-[0.75rem]">
                      {run.id.slice(0, 8)}
                    </td>
                    <td>{run.provider}</td>
                    <td>{run.model}</td>
                    <td>
                      <span className={`status-${run.status === "pass" ? "pass" : run.status === "fail" ? "fail" : "run"}`}>
                        {run.status.toUpperCase()}
                      </span>
                    </td>
                    <td style={{ color: "var(--acid-green)" }}>{run.passed}</td>
                    <td style={{ color: "var(--electric-red)" }}>{run.failed}</td>
                    <td className="font-bold">{run.score !== null ? `${run.score}%` : "—"}</td>
                    <td className="text-[var(--text-muted)] text-[0.75rem]">
                      {run.created_at ? new Date(run.created_at).toLocaleString() : "—"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </>
  );
}
