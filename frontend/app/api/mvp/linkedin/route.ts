import { NextResponse } from "next/server";

type Post = {
  id: number;
  author: string;
  text: string;
  createdAt: string;
};

const posts: Post[] = [
  {
    id: 1,
    author: "Placement Cell",
    text: "Infosys internship applications for 2026 batch are now open.",
    createdAt: new Date().toISOString(),
  },
];

export async function GET() {
  return NextResponse.json({ posts: [...posts].reverse() });
}

export async function POST(req: Request) {
  const body = await req.json();
  const text = String(body?.text || "").trim();
  const author = String(body?.author || "GGSIPU Fresher").trim();

  if (!text) {
    return NextResponse.json({ error: "Text is required" }, { status: 400 });
  }

  posts.push({
    id: Date.now(),
    author,
    text,
    createdAt: new Date().toISOString(),
  });

  return NextResponse.json({ ok: true });
}
