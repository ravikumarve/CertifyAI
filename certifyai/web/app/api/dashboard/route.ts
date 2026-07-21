import { NextRequest, NextResponse } from "next/server";
import { execSync } from "child_process";
import path from "path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const mode = searchParams.get("mode") || "dashboard";

    const dbScript = path.join(process.cwd(), "lib", "db_query.py");
    const dbPath = path.join(process.cwd(), "..", "..", "certifyai.db");

    const result = execSync(
      `python3 "${dbScript}" "${dbPath}" ${mode}`,
      { encoding: "utf-8", timeout: 10000 }
    );

    const data = JSON.parse(result);
    return NextResponse.json(data);
  } catch (err) {
    console.error("Dashboard API error:", err);
    return NextResponse.json(
      { error: String(err) },
      { status: 500 }
    );
  }
}
