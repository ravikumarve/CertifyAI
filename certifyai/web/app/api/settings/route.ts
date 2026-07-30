import { NextRequest, NextResponse } from "next/server";
import { execSync } from "child_process";
import path from "path";

export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const scriptPath = path.join(process.cwd(), "lib", "config_io.py");

export async function GET() {
  try {
    const stdout = execSync(`python3 "${scriptPath}" read`, { timeout: 10000, encoding: "utf-8" });
    const data = JSON.parse(stdout);
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error("Settings GET error:", msg);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const jsonStr = JSON.stringify(body);
    const stdout = execSync(`python3 "${scriptPath}" write`, {
      timeout: 10000,
      encoding: "utf-8",
      input: jsonStr,
    });
    const data = JSON.parse(stdout);
    if (data.error) {
      return NextResponse.json(data, { status: 400 });
    }
    return NextResponse.json(data);
  } catch (err: unknown) {
    const msg = err instanceof Error ? err.message : String(err);
    console.error("Settings POST error:", msg);
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
