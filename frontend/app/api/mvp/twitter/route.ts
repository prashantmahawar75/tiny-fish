import { NextResponse } from "next/server";

type Tweet = {
  id: number;
  author: string;
  text: string;
  createdAt: string;
};

const tweets: Tweet[] = [
  {
    id: 1,
    author: "campus_builder",
    text: "Launching the real-time Twitter MVP for creators.",
    createdAt: new Date().toISOString(),
  },
];

export async function GET() {
  return NextResponse.json({ tweets: [...tweets].reverse() });
}

export async function POST(req: Request) {
  const body = await req.json();
  const text = String(body?.text || "").trim();
  const author = String(body?.author || "you").trim();

  if (!text) {
    return NextResponse.json({ error: "Text is required" }, { status: 400 });
  }

  tweets.push({
    id: Date.now(),
    author,
    text,
    createdAt: new Date().toISOString(),
  });

  return NextResponse.json({ ok: true });
}
