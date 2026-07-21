"use client";

import { useEffect, useState, useCallback } from "react";
import StatsCards from "@/components/stats-cards";
import TrendChart from "@/components/trend-chart";
import type { DashboardData } from "@/lib/types";

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const res = await fetch("/api/dashboard");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      if (json.error) throw new Error(json.error);
      setData(json);
    } catch (err) {
      setError(String(err));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, [fetchData]);

  const stats = data?.stats;
  const runningTime = stats?.running_time_secs
    ? `${Math.floor(stats.running_time_secs / 60)}:${String(stats.running_time_secs % 60).padStart(2, "0")}`
    : "—";

  return (
    <>
      {/* Top Bar */}
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Dashboard
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            {stats?.provider && stats?.model
              ? `Last run: ${stats.provider} / ${stats.model}`
              : "Monitoring AI runtime compliance"}
          </div>
        </div>
        {error && (
          <div className="flex items-center gap-2">
            <span className="text-[var(--electric-red)] text-[0.75rem] font-[family-name:var(--font-mono)]">
              {error}
            </span>
            <button
              onClick={fetchData}
              className="brut-btn text-[0.7rem] px-3 py-1"
            >
              RETRY
            </button>
          </div>
        )}
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-3 text-[var(--text-muted)] font-[family-name:var(--font-mono)]">
          <div className="w-6 h-6 border-2 border-[var(--border-hard)] border-t-[var(--acid-green)] rounded-full animate-spin" />
          <span className="text-[0.8rem]">Loading dashboard...</span>
        </div>
      ) : (
        <>
          {/* Stats Cards */}
          <StatsCards
            score={stats?.score ?? null}
            passed={stats?.passed ?? 0}
            failed={stats?.failed ?? 0}
            runningTime={runningTime}
          />

          {/* Score Trend Chart */}
          <TrendChart />

          {/* Recent Results Table */}
          <div className="bg-[var(--bg-void)] border border-[var(--border-hard)]">
            <div className="px-4 py-3 border-b border-[var(--border-hard)] bg-[var(--bg-panel)] flex justify-between font-[family-name:var(--font-mono)] text-[0.75rem] uppercase">
              <span>Recent Results</span>
              <span style={{ color: "var(--cyber-blue)" }}>
                {stats?.total ?? 0} TOTAL ATTACKS
              </span>
            </div>
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

          {/* System Info Grid */}
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
