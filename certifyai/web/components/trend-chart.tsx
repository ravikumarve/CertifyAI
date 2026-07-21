"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import { useEffect, useState } from "react";

interface RunDataPoint {
  id: string;
  score: number | null;
  time: string;            // formatted display time
  ts: number;              // epoch ms for sorting
  passed: number;
  failed: number;
  provider: string;
  model: string;
}

export default function TrendChart() {
  const [data, setData] = useState<RunDataPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/dashboard?mode=runs")
      .then((r) => r.json())
      .then((json) => {
        const points: RunDataPoint[] = (json.runs ?? []).map((run: Record<string, unknown>) => {
          const created = String(run.created_at ?? "");
          const ts = new Date(created).getTime();
          const d = new Date(ts);
          const time = isNaN(ts)
            ? "—"
            : `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
          return {
            id: String(run.id).slice(0, 8),
            score: run.score != null ? Number(run.score) : null,
            time,
            ts,
            passed: Number(run.passed ?? 0),
            failed: Number(run.failed ?? 0),
            provider: String(run.provider ?? "—"),
            model: String(run.model ?? "—"),
          };
        });
        points.sort((a, b) => a.ts - b.ts);
        setData(points);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="brut-card min-h-[220px] justify-center items-center">
        <div className="text-[var(--text-muted)] font-[family-name:var(--font-mono)] text-[0.75rem]">
          Loading trend...
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="brut-card min-h-[220px] justify-center items-center">
        <div className="text-[var(--text-faint)] font-[family-name:var(--font-mono)] text-[0.75rem] italic">
          No run data yet.
        </div>
      </div>
    );
  }

  const hasScores = data.some((d) => d.score !== null && d.score > 0);
  const chartData = hasScores ? data.filter((d) => d.score !== null) : data;

  return (
    <div className="brut-card">
      <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
        Score Trend
      </div>
      <div className="w-full" style={{ height: 220 }}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: -8 }}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="var(--border-hard)"
              vertical={false}
            />
            <XAxis
              dataKey="time"
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
              axisLine={{ stroke: "var(--border-hard)" }}
              tickLine={false}
            />
            <YAxis
              domain={[0, 100]}
              tick={{ fill: "var(--text-faint)", fontSize: 11, fontFamily: "JetBrains Mono, monospace" }}
              axisLine={false}
              tickLine={false}
              tickFormatter={(v: number) => `${v}%`}
              width={40}
            />
            <Tooltip
              contentStyle={{
                background: "var(--bg-panel)",
                border: "1px solid var(--border-hard)",
                borderRadius: 0,
                fontSize: 12,
                fontFamily: "JetBrains Mono, monospace",
                color: "var(--text-main)",
              }}
              labelStyle={{ color: "var(--text-muted)", marginBottom: 4 }}
              formatter={(value, name) => {
                if (name === "score" && typeof value === "number") return [`${value}%`, "Score"];
                return [value ?? "—", name];
              }}
            />
            <Line
              type="monotone"
              dataKey="score"
              stroke="var(--acid-green)"
              strokeWidth={2}
              dot={{ fill: "var(--acid-green)", strokeWidth: 0, r: 3 }}
              activeDot={{ fill: "var(--acid-green)", stroke: "var(--bg-void)", strokeWidth: 2, r: 5 }}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
