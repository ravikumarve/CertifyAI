"use client";

import { useEffect, useState, useMemo } from "react";
import type { RunSummary } from "@/lib/types";

type SortKey = "date" | "score_asc" | "score_desc";
type StatusFilter = "all" | "pass" | "fail" | "running" | "error";

export default function ResultsPage() {
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");
  const [sortBy, setSortBy] = useState<SortKey>("date");

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

  const filtered = useMemo(() => {
    let list = [...runs];

    // Text search — match ID, provider, model
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter(
        (r) =>
          r.id.toLowerCase().includes(q) ||
          r.provider.toLowerCase().includes(q) ||
          r.model.toLowerCase().includes(q)
      );
    }

    // Status filter
    if (statusFilter !== "all") {
      list = list.filter((r) => r.status.toLowerCase() === statusFilter);
    }

    // Sort
    switch (sortBy) {
      case "date":
        list.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        break;
      case "score_asc":
        list.sort((a, b) => (a.score ?? 0) - (b.score ?? 0));
        break;
      case "score_desc":
        list.sort((a, b) => (b.score ?? 0) - (a.score ?? 0));
        break;
    }

    return list;
  }, [runs, search, statusFilter, sortBy]);

  return (
    <>
      {/* Top Bar */}
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Results History
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            {loading ? "Loading..." : `${filtered.length} of ${runs.length} runs`}
          </div>
        </div>
        {error && (
          <div className="text-[var(--electric-red)] text-[0.75rem] font-[family-name:var(--font-mono)]">
            {error}
          </div>
        )}
      </div>

      {/* Search + Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        {/* Search input */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search by ID, provider, model..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full px-4 py-2 bg-[var(--bg-void)] border border-[var(--border-hard)] text-[var(--text-main)]
              font-[family-name:var(--font-mono)] text-[0.8rem] outline-none
              placeholder:text-[var(--text-faint)]
              focus:border-[var(--border-focus)] transition-colors"
          />
        </div>

        {/* Status Filter */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
          className="px-3 py-2 bg-[var(--bg-void)] border border-[var(--border-hard)] text-[var(--text-main)]
            font-[family-name:var(--font-mono)] text-[0.8rem] uppercase outline-none
            focus:border-[var(--border-focus)] transition-colors cursor-pointer"
        >
          <option value="all">All Status</option>
          <option value="pass">Pass</option>
          <option value="fail">Fail</option>
          <option value="running">Running</option>
          <option value="error">Error</option>
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value as SortKey)}
          className="px-3 py-2 bg-[var(--bg-void)] border border-[var(--border-hard)] text-[var(--text-main)]
            font-[family-name:var(--font-mono)] text-[0.8rem] uppercase outline-none
            focus:border-[var(--border-focus)] transition-colors cursor-pointer"
        >
          <option value="date">Sort: Newest</option>
          <option value="score_desc">Sort: Score ↓</option>
          <option value="score_asc">Sort: Score ↑</option>
        </select>
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
                <th>Errors</th>
                <th>Score</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-[var(--text-muted)] text-center py-8">
                    {runs.length === 0 ? "No runs yet." : "No runs match your filters."}
                  </td>
                </tr>
              ) : (
                filtered.map((run) => (
                  <tr key={run.id}>
                    <td className="font-[family-name:var(--font-mono)] text-[0.75rem]">
                      {run.id.slice(0, 8)}
                    </td>
                    <td>{run.provider}</td>
                    <td>{run.model}</td>
                    <td>
                      <StatusBadge status={run.status} />
                    </td>
                    <td style={{ color: "var(--acid-green)" }}>{run.passed}</td>
                    <td style={{ color: "var(--electric-red)" }}>{run.failed}</td>
                    <td className="text-[var(--text-muted)]">{run.errors ?? 0}</td>
                    <td className="font-bold">{run.score !== null ? `${run.score}%` : "—"}</td>
                    <td className="text-[var(--text-muted)] text-[0.75rem]">
                      {run.created_at ? formatDate(run.created_at) : "—"}
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

function StatusBadge({ status }: { status: string }) {
  const s = status.toLowerCase();
  let cls = "";
  if (s === "pass" || s === "completed") cls = "status-pass";
  else if (s === "fail") cls = "status-fail";
  else if (s === "running") cls = "status-run";
  else if (s === "error") cls = "text-[var(--electric-red)] font-bold";

  return <span className={cls}>{status.toUpperCase()}</span>;
}

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return iso;
  }
}
