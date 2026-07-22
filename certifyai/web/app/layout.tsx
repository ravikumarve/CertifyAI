import type { Metadata } from "next";
import "./globals.css";
import Sidebar from "@/components/sidebar";

export const metadata: Metadata = {
  title: "CertifyAI | Operations Center",
  description: "Continuous Compliance Engine for AI Runtimes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="flex min-h-screen">
        <div className="sticky top-0 h-screen shrink-0">
          <Sidebar />
        </div>
        <main className="flex-1 bg-[var(--bg-surface)] flex flex-col min-h-screen overflow-y-auto">
          <div className="p-8 flex flex-col gap-6 flex-1 min-h-0">
            {children}
          </div>
        </main>
      </body>
    </html>
  );
}
