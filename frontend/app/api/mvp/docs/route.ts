import { NextResponse } from "next/server";

let sharedDoc = "# GGSIPU Collaboration Doc\n\nStart writing together in real-time.";
let updatedAt = new Date().toISOString();

export async function GET() {
  return NextResponse.json({ content: sharedDoc, updatedAt });
}

export async function PUT(req: Request) {
  const body = await req.json();
  const content = String(body?.content || "");

  sharedDoc = content;
  updatedAt = new Date().toISOString();

  return NextResponse.json({ ok: true, updatedAt });
}
