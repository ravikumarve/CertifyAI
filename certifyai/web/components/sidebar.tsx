"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "Dashboard", id: "dashboard" },
  { href: "/", label: "Run Attack", id: "run" },
  { href: "/results", label: "Results", id: "results" },
  { href: "/settings", label: "Settings", id: "settings" },
];

export default function Sidebar() {
  const pathname = usePathname();

  function isActive(item: typeof NAV_ITEMS[0]): boolean {
    if (item.href === "/") {
      // On /, highlight Run Attack (not Dashboard) to match mockup
      return item.id === "run" && pathname === "/";
    }
    return pathname === item.href;
  }

  return (
    <aside className="w-[260px] bg-[var(--bg-void)] border-r border-[var(--border-hard)] flex flex-col p-6 z-10">
      <Link href="/" className="flex items-center gap-3 font-[family-name:var(--font-mono)] text-[1.1rem] font-extrabold text-[var(--text-main)] mb-12 no-underline tracking-tight">
        <div className="w-4 h-4 bg-[var(--acid-green)]"></div>
        CERTIFYAI
      </Link>

      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map((item) => {
          const active = isActive(item);
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`flex items-center justify-between px-4 py-3 border border-transparent
                text-[var(--text-muted)] font-medium text-[0.85rem] no-underline transition-all duration-200
                font-[family-name:var(--font-mono)] uppercase tracking-wider
                ${active ? "bg-[var(--bg-panel)] text-[var(--text-main)] border-[var(--border-focus)] border-l-[3px] border-l-[var(--acid-green)]" : ""}
                hover:text-[var(--text-main)] hover:bg-[var(--bg-surface)] hover:border-[var(--border-hard)]`}
            >
              <span>{item.label}</span>
              {item.id === "run" && (
                <span className="text-[0.7rem] text-[var(--acid-green)]">LIVE</span>
              )}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto p-4 bg-[var(--bg-surface)] border border-[var(--border-hard)] flex flex-col gap-2 text-[0.7rem] text-[var(--text-muted)] font-[family-name:var(--font-mono)] uppercase">
        <div className="flex justify-between">
          <span>Engine:</span>
          <span id="sys-engine" className="text-[var(--acid-green)]">ONLINE</span>
        </div>
        <div className="flex justify-between">
          <span>Vault:</span>
          <span id="sys-vault" className="text-[var(--text-main)]">LOADING</span>
        </div>
        <div className="flex justify-between">
          <span>Version:</span>
          <span id="sys-version" className="text-[var(--text-main)]">v1.0.4</span>
        </div>
      </div>
    </aside>
  );
}
