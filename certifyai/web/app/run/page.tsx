"use client";

import { useEffect, useState } from "react";
import AttackTable from "@/components/attack-table";
import VaultLog from "@/components/vault-log";
import type { DashboardData } from "@/lib/types";

export default function RunAttackPage() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
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
    }
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const stats = data?.stats;
  const isRunning = data?.current_run?.status === "running";

  return (
    <>
      {/* Top Bar */}
      <div className="flex justify-between items-end pb-6 border-b border-[var(--border-hard)]">
        <div>
          <div className="font-[family-name:var(--font-mono)] text-[1.5rem] font-bold uppercase tracking-tight">
            Attack Execution
          </div>
          <div className="text-[var(--text-muted)] text-[0.85rem] mt-1 font-[family-name:var(--font-mono)]">
            Target: {stats?.provider ?? "—"} / {stats?.model ?? "—"}
          </div>
        </div>
        <div className="flex gap-3">
          {error && (
            <div className="text-[var(--electric-red)] text-[0.75rem] font-[family-name:var(--font-mono)]">
              DB: {error}
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex items-center justify-center text-[var(--text-muted)] font-[family-name:var(--font-mono)]">
          Loading attack view...
        </div>
      ) : (
        <div className="grid grid-cols-[2fr_1fr] gap-4 flex-1 min-h-0">
          <AttackTable
            results={data?.recent_results ?? []}
            frameworks={data?.current_run?.frameworks ?? stats?.frameworks ?? []}
            concurrency={data?.current_run?.concurrency}
            isRunning={isRunning}
            completedCount={data?.recent_results?.length ?? 0}
            totalCount={stats?.total ?? 0}
          />
          <VaultLog entries={data?.vault_log ?? []} />
        </div>
      )}
    </>
  );
}
