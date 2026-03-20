import { NextResponse } from "next/server";

type Tip = {
  id: number;
  creator: string;
  amount: number;
  upiId: string;
  createdAt: string;
};

const tips: Tip[] = [];

export async function GET() {
  return NextResponse.json({ tips: [...tips].reverse() });
}

export async function POST(req: Request) {
  const body = await req.json();
  const creator = String(body?.creator || "creator").trim();
  const amount = Number(body?.amount || 0);

  if (!amount || amount <= 0) {
    return NextResponse.json({ error: "Valid amount is required" }, { status: 400 });
  }

  const tip = {
    id: Date.now(),
    creator,
    amount,
    upiId: `${creator.replace(/\s+/g, "").toLowerCase()}@upi`,
    createdAt: new Date().toISOString(),
  };

  tips.push(tip);

  return NextResponse.json({ ok: true, tip });
}
