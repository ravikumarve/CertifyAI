"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", id: "dashboard" },
  { href: "/run", label: "Run Attack", id: "run" },
  { href: "/results", label: "Results", id: "results" },
  { href: "/settings", label: "Settings", id: "settings" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const [status, setStatus] = useState({
    engine: "ONLINE",
    vault: "LOADING",
    version: "v1.0.4",
  });

  useEffect(() => {
    let mounted = true;
    async function fetchStatus() {
      try {
        const res = await fetch("/api/dashboard");
        if (!res.ok) return;
        const data = await res.json();
        if (!mounted) return;
        if (data.stats) {
          setStatus({
            engine: data.stats.engine_status || "ONLINE",
            vault: data.stats.vault_status || "—",
            version: data.stats.version || "v0.1.0",
          });
        }
      } catch {
        // best-effort
      }
    }
    fetchStatus();
    const interval = setInterval(fetchStatus, 10000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <aside className="w-[260px] bg-[var(--bg-void)] border-r border-[var(--border-hard)] flex flex-col p-6 z-10">
      {/* Brand */}
      <Link
        href="/"
        className="flex items-center gap-3 font-[family-name:var(--font-mono)] text-[1.1rem] font-extrabold text-[var(--text-main)] mb-12 no-underline tracking-tight group"
      >
        <div className="w-4 h-4 bg-[var(--acid-green)] group-hover:shadow-[0_0_12px_var(--acid-green)] transition-shadow duration-300"></div>
        CERTIFYAI
      </Link>

      {/* Nav */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`
                flex items-center gap-3 px-4 py-3 no-underline
                font-[family-name:var(--font-mono)] text-[0.85rem] uppercase tracking-wider
                transition-all duration-200
                ${
                  active
                    ? "bg-[var(--bg-panel)] text-[var(--text-main)] border-l-[3px] border-l-[var(--acid-green)]"
                    : "text-[var(--text-muted)] border-l-[3px] border-l-transparent hover:text-[var(--text-main)] hover:bg-[var(--bg-surface)]"
                }
              `}
            >
              {/* Active dot */}
              <span
                className={`w-1.5 h-1.5 rounded-full transition-all duration-200 ${
                  active ? "bg-[var(--acid-green)] shadow-[0_0_6px_var(--acid-green)]" : "bg-transparent"
                }`}
              />
              <span>{item.label}</span>
              {item.id === "run" && (
                <span className="ml-auto text-[0.7rem] text-[var(--acid-green)]">LIVE</span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Status Panel */}
      <div className="mt-auto p-4 bg-[var(--bg-surface)] border border-[var(--border-hard)] flex flex-col gap-2.5 text-[0.7rem] font-[family-name:var(--font-mono)] uppercase">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              status.engine === "ONLINE" ? "bg-[var(--acid-green)]" : "bg-[var(--electric-red)]"
            }`}
          />
          <span className="text-[var(--text-muted)]">Engine:</span>
          <span
            className={`ml-auto ${
              status.engine === "ONLINE" ? "text-[var(--acid-green)]" : "text-[var(--electric-red)]"
            }`}
          >
            {status.engine}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full ${
              status.vault === "EMPTY" ? "bg-[var(--text-faint)]" : "bg-[var(--cyber-blue)]"
            }`}
          />
          <span className="text-[var(--text-muted)]">Vault:</span>
          <span className="ml-auto text-[var(--text-main)]">{status.vault}</span>
        </div>
        <div className="flex items-center gap-2 pt-1 border-t border-[var(--border-hard)]">
          <span className="text-[var(--text-muted)]">Version:</span>
          <span className="ml-auto text-[var(--text-main)]">{status.version}</span>
        </div>
      </div>
    </aside>
  );
}
