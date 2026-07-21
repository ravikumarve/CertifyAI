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
      <body className="flex h-screen overflow-hidden">
        <Sidebar />
        <main className="flex-1 p-8 overflow-y-auto bg-[var(--bg-surface)] flex flex-col gap-6">
          {children}
        </main>
      </body>
    </html>
  );
}
