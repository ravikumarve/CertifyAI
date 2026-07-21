import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";
import fs from "fs";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const execAsync = promisify(exec);

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams;
  const mode = searchParams.get("mode") || "dashboard";

  const dbScript = path.join(process.cwd(), "lib", "db_query.py");
  const dbPath = path.join(process.cwd(), "..", "..", "certifyai.db");

  // Debug: check if files exist
  const scriptExists = fs.existsSync(dbScript);
  const dbExists = fs.existsSync(dbPath);

  if (!scriptExists) {
    return NextResponse.json({ error: `Script not found: ${dbScript}` }, { status: 500 });
  }
  if (!dbExists) {
    return NextResponse.json({ error: `Database not found: ${dbPath}` }, { status: 500 });
  }

  try {
    const { stdout, stderr } = await execAsync(
      `python3 "${dbScript}" "${dbPath}" ${mode}`,
      { timeout: 15000 }
    );

    if (stderr) {
      console.error("Python stderr:", stderr);
    }

    const data = JSON.parse(stdout);
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    const stderr = (err as { stderr?: string }).stderr || "";
    console.error("Dashboard API error:", msg, stderr);
    return NextResponse.json(
      { error: msg, stderr },
      { status: 500 }
    );
  }
}
