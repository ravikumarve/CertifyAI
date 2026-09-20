"use client";

import { useEffect, useState } from "react";
import TrendChart from "@/components/trend-chart";
import type { DashboardData, RunSummary } from "@/lib/types";

function shortId(id: string): string {
  return id.length > 8 ? id.slice(0, 8) : id;
}

function scoreColor(score: number | null): string {
  if (score === null) return "var(--text-muted)";
  if (score >= 70) return "var(--acid-green)";
  if (score >= 40) return "var(--amber, #FFB800)";
  return "var(--electric-red)";
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

function runScoreClass(score: number | null): string {
  if (score === null) return "txt-muted";
  if (score >= 70) return "txt-pass";
  if (score >= 40) return "txt-amber";
  return "txt-fail";
}

function statusClass(status: string): string {
  switch (status.toLowerCase()) {
    case "pass": return "status-pass";
    case "fail": return "status-fail";
    case "running": return "status-run";
    default: return "";
  }
}

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [runs, setRuns] = useState<RunSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Polling subscription: fetch-on-mount + 5s refresh with unmount guard.
  // (fetchers live inside the effect so state only settles after await.)
  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      try {
        const res = await fetch("/api/dashboard");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const json = await res.json();
        if (json.error) throw new Error(json.error);
        if (!cancelled) {
          setData(json);
          setError(null);
        }
      } catch (err) {
        if (!cancelled) setError(String(err));
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    async function fetchRuns() {
      try {
        const res = await fetch("/api/dashboard?mode=runs");
        if (!res.ok) return;
        const json = await res.json();
        if (!cancelled && json.runs) setRuns(json.runs.slice(0, 5));
      } catch {
        // best-effort
      }
    }

    fetchData();
    fetchRuns();
    const interval = setInterval(() => {
      fetchData();
      fetchRuns();
    }, 5000);
    return () => {
      cancelled = true;
      clearInterval(interval);
    };
  }, []);

  const stats = data?.stats;
  const score = stats?.score ?? null;
  const sColor = scoreColor(score);

  return (
    <>
      {/* Top Bar — with New Run button */}
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Dashboard
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            Compliance overview
          </div>
        </div>
        <div className="flex items-center gap-3">
          {error && (
            <span className="text-[var(--electric-red)] text-[0.75rem] font-[family-name:var(--font-mono)]">
              {error}
            </span>
          )}
          <a href="/run">
            <button className="brut-btn brut-btn-primary">New Run</button>
          </a>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-[var(--text-muted)] font-[family-name:var(--font-mono)]">
          <div className="w-6 h-6 border-2 border-[var(--border-hard)] border-t-[var(--acid-green)] rounded-full animate-spin" />
          <span className="text-[0.8rem]">Loading dashboard...</span>
        </div>
      ) : (
        <>
          {/* ── 4 Stat Cards (matching mockup) ── */}
          <div className="grid grid-cols-4 gap-4">
            {/* Card 1: Last Run */}
            <div className="brut-card active">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Last Run
              </div>
              <div
                className="text-[1.5rem] font-bold font-[family-name:var(--font-mono)] leading-none mb-2"
                style={{ color: "var(--cyber-blue)" }}
              >
                {stats?.last_run_id ? shortId(stats.last_run_id) : "—"}
              </div>
              <div className="text-[0.75rem] text-[var(--text-faint)] font-[family-name:var(--font-mono)] uppercase">
                {stats?.last_run_created_at
                  ? new Date(stats.last_run_created_at).toLocaleString()
                  : "No runs yet"}
              </div>
            </div>

            {/* Card 2: Attacks */}
            <div className="brut-card">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Attacks
              </div>
              <div className="text-[2rem] font-bold font-[family-name:var(--font-mono)] leading-none mb-2">
                {stats?.total ?? 0}
              </div>
              <div className="text-[0.75rem] text-[var(--text-faint)] font-[family-name:var(--font-mono)] uppercase">
                6 categories // 18 scenarios
              </div>
            </div>

            {/* Card 3: Last Score */}
            <div className={`brut-card${score !== null && score < 40 ? " danger" : ""}`}>
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Last Score
              </div>
              <div
                className="text-[2rem] font-bold font-[family-name:var(--font-mono)] leading-none mb-2"
                style={{ color: sColor }}
              >
                {score !== null ? `${score}%` : "—"}
              </div>
              <div className="text-[0.75rem] text-[var(--text-faint)] font-[family-name:var(--font-mono)] uppercase">
                {stats ? `${stats.passed ?? 0} passed // ${stats.failed ?? 0} failed` : "—"}
              </div>
            </div>

            {/* Card 4: Vault */}
            <div className="brut-card">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Vault
              </div>
              <div
                className="text-[1.5rem] font-bold font-[family-name:var(--font-mono)] leading-none mb-2"
                style={{ color: "var(--acid-green)" }}
              >
                {stats?.vault_status ?? "—"}
              </div>
              <div className="text-[0.75rem] text-[var(--text-faint)] font-[family-name:var(--font-mono)] uppercase">
                SHA-256 chain intact
              </div>
            </div>
          </div>

          {/* Score Trend Chart */}
          <TrendChart />

          {/* ── Two-Column Table Grid ── */}
          <div className="grid grid-cols-2 gap-4">
            {/* Left: Recent Results (Latest Run) — attack-level */}
            <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col min-h-0">
              <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-panel)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase shrink-0">
                <span>Recent Results (Latest Run)</span>
                <span style={{ color: "var(--cyber-blue)" }}>
                  {stats?.total ?? 0} ATTACKS
                  {stats && stats.all_time_total > (stats.total ?? 0) && (
                    <span className="ml-2 text-[var(--text-faint)] font-normal">
                      ({stats.all_time_passed} passed / {stats.all_time_total} total all-time)
                    </span>
                  )}
                </span>
              </div>
              <div className="overflow-y-auto flex-1 min-h-0">
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
                    {(data?.recent_results ?? []).length === 0 ? (
                      <tr>
                        <td colSpan={4} className="text-[var(--text-muted)] text-center py-8">
                          No results yet. Run an attack from the{" "}
                          <a href="/run" className="text-[var(--cyber-blue)] underline">
                            Run Attack
                          </a>{" "}
                          page.
                        </td>
                      </tr>
                    ) : (
                      data?.recent_results.slice(0, 15).map((r) => (
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
                            <span className={statusClass(r.status)}>
                              {r.status}
                            </span>
                            {r.response_time_ms != null && (
                              <span className="ml-2 text-[0.65rem] text-[var(--text-faint)]">
                                {r.response_time_ms}ms
                              </span>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Right: Recent Runs — run-level summaries */}
            <div className="bg-[var(--bg-void)] border border-[var(--border-hard)] flex flex-col min-h-0">
              <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-panel)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase shrink-0">
                <span>Recent Runs</span>
                <span style={{ color: "var(--text-muted)" }}>LAST 5</span>
              </div>
              <div className="overflow-y-auto flex-1 min-h-0">
                <table className="brut-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Date</th>
                      <th>Status</th>
                      <th>Score</th>
                      <th>Total</th>
                      <th>Passed</th>
                      <th>Failed</th>
                    </tr>
                  </thead>
                  <tbody>
                    {runs.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="text-[var(--text-muted)] text-center py-8">
                          No runs yet.{" "}
                          <a href="/run" className="text-[var(--cyber-blue)] underline">
                            Start an attack
                          </a>
                        </td>
                      </tr>
                    ) : (
                      runs.map((r) => (
                        <tr key={r.id}>
                          <td>{shortId(r.id)}</td>
                          <td>
                            {r.created_at
                              ? new Date(r.created_at).toLocaleString()
                              : "—"}
                          </td>
                          <td className="txt-muted">{r.status}</td>
                          <td className={`status-txt ${runScoreClass(r.score)}`}>
                            {r.score !== null ? `${r.score}%` : "—"}
                          </td>
                          <td>{r.total ?? 0}</td>
                          <td>{r.passed ?? 0}</td>
                          <td>{r.failed ?? 0}</td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ── System Info Grid (Engine, Vault, Frameworks) ── */}
          <div className="grid grid-cols-3 gap-4">
            <div className="brut-card">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Engine
              </div>
              <div
                className="text-[1.2rem] font-bold font-[family-name:var(--font-mono)] flex items-center gap-2"
                style={{ color: "var(--acid-green)" }}
              >
                <span className="w-2 h-2 rounded-full bg-[var(--acid-green)]" />
                {stats?.engine_status ?? "—"}
              </div>
            </div>
            <div className="brut-card">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Vault
              </div>
              <div className="text-[1.2rem] font-bold font-[family-name:var(--font-mono)]">
                {stats?.vault_status ?? "—"}
              </div>
            </div>
            <div className="brut-card">
              <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
                Frameworks
              </div>
              <div
                className="text-[0.9rem] font-bold font-[family-name:var(--font-mono)]"
                style={{ color: "var(--cyber-blue)" }}
              >
                {stats?.frameworks?.join(", ") || "—"}
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
