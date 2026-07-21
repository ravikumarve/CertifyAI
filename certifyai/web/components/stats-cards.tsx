"use client";

interface StatsCardsProps {
  score: number | null;
  passed: number;
  failed: number;
  runningTime: string;
}

export default function StatsCards({ score, passed, failed, runningTime }: StatsCardsProps) {
  const cards = [
    {
      label: "Compliance Score",
      value: score !== null ? `${score}%` : "—",
      desc: "Latest Run",
      accent: "active" as const,
      color: score !== null && score >= 70 ? "var(--acid-green)" : "var(--electric-red)",
    },
    {
      label: "Tests Passed",
      value: String(passed),
      desc: "Verified Secure",
      accent: "success" as const,
      color: "var(--text-main)",
    },
    {
      label: "Tests Failed",
      value: String(failed),
      desc: "Vulnerabilities Found",
      accent: "danger" as const,
      color: "var(--electric-red)",
    },
    {
      label: "Running Time",
      value: runningTime,
      desc: "Elapsed",
      accent: "default" as const,
      color: "var(--text-main)",
    },
  ];

  return (
    <div className="grid grid-cols-4 gap-4">
      {cards.map((card) => (
        <div key={card.label} className={`brut-card ${card.accent !== "default" ? card.accent : ""}`}>
          <div className="text-[0.75rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase tracking-wider mb-4">
            {card.label}
          </div>
          <div
            className="text-[2rem] font-bold font-[family-name:var(--font-mono)] leading-none mb-2"
            style={{ color: card.color }}
          >
            {card.value}
          </div>
          <div className="text-[0.75rem] text-[var(--text-faint)] font-[family-name:var(--font-mono)] uppercase">
            {card.desc}
          </div>
        </div>
      ))}
    </div>
  );
}
