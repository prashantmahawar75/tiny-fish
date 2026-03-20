"use client";

import { useEffect, useMemo, useState } from "react";

type Tweet = {
  id: number;
  author: string;
  text: string;
  createdAt: string;
};

type Tip = {
  id: number;
  creator: string;
  amount: number;
  upiId: string;
  createdAt: string;
};

const projectLinks = [
  {
    name: "Twitter Clone",
    github: process.env.NEXT_PUBLIC_TWITTER_GITHUB || "",
    live: process.env.NEXT_PUBLIC_TWITTER_LIVE || "",
  },
  {
    name: "Instagram Reels + UPI",
    github: process.env.NEXT_PUBLIC_REELS_GITHUB || "",
    live: process.env.NEXT_PUBLIC_REELS_LIVE || "",
  },
  {
    name: "Meesho Social Commerce",
    github: process.env.NEXT_PUBLIC_MEESHO_GITHUB || "",
    live: process.env.NEXT_PUBLIC_MEESHO_LIVE || "",
  },
  {
    name: "Notion Collaborative Docs",
    github: process.env.NEXT_PUBLIC_DOCS_GITHUB || "",
    live: process.env.NEXT_PUBLIC_DOCS_LIVE || "",
  },
  {
    name: "LinkedIn for GGSIPU",
    github: process.env.NEXT_PUBLIC_LINKEDIN_GITHUB || "",
    live: process.env.NEXT_PUBLIC_LINKEDIN_LIVE || "",
  },
];

const reels = [
  { id: 1, creator: "@dance.with.diya", title: "Campus dance reel" },
  { id: 2, creator: "@code.by.karan", title: "React in 30 seconds" },
  { id: 3, creator: "@foodie.rana", title: "Street food hunt" },
];

const products = [
  { id: 1, name: "Handmade Jhumka", price: 299, seller: "Neha Store" },
  { id: 2, name: "Minimal Hoodie", price: 799, seller: "Campus Threads" },
  { id: 3, name: "Desk Organizer", price: 349, seller: "StudyKart" },
];

const jobs = [
  { id: 1, role: "Frontend Intern", company: "Zomato", stipend: "25k/month" },
  { id: 2, role: "SDE Trainee", company: "Infosys", stipend: "6 LPA" },
  { id: 3, role: "Data Analyst Intern", company: "Paytm", stipend: "30k/month" },
];

export default function MvpLabPage() {
  const [tweets, setTweets] = useState<Tweet[]>([]);
  const [tweetText, setTweetText] = useState("");

  const [tipAmount, setTipAmount] = useState(49);
  const [tipCreator, setTipCreator] = useState("dance.with.diya");
  const [tips, setTips] = useState<Tip[]>([]);

  const [cartCount, setCartCount] = useState(0);
  const [sharedDoc, setSharedDoc] = useState("");
  const [docSavedAt, setDocSavedAt] = useState("");

  const [linkedinPosts, setLinkedinPosts] = useState<Tweet[]>([]);
  const [linkedinText, setLinkedinText] = useState("");

  const upiCheckoutLink = useMemo(() => {
    const amount = Math.max(1, cartCount * 199);
    return `upi://pay?pa=tinyfish@upi&pn=TinyFish%20Store&am=${amount}&cu=INR`;
  }, [cartCount]);

  const loadTweets = async () => {
    const res = await fetch("/api/mvp/twitter");
    const data = await res.json();
    setTweets(data.tweets || []);
  };

  const loadTips = async () => {
    const res = await fetch("/api/mvp/reels-tip");
    const data = await res.json();
    setTips(data.tips || []);
  };

  const loadDoc = async () => {
    const res = await fetch("/api/mvp/docs");
    const data = await res.json();
    setSharedDoc(data.content || "");
    setDocSavedAt(data.updatedAt || "");
  };

  const loadLinkedin = async () => {
    const res = await fetch("/api/mvp/linkedin");
    const data = await res.json();
    setLinkedinPosts(data.posts || []);
  };

  useEffect(() => {
    loadTweets();
    loadTips();
    loadDoc();
    loadLinkedin();

    const timer = setInterval(() => {
      loadTweets();
      loadTips();
      loadDoc();
      loadLinkedin();
    }, 2500);

    return () => clearInterval(timer);
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-slate-100 px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <section className="rounded-2xl border border-slate-700 p-6 bg-slate-900">
          <h1 className="text-3xl font-bold">Hardcore MVP Clone Suite</h1>
          <p className="text-slate-400 mt-2">
            Five Vercel-compatible mini products: real-time social, reels tipping, social commerce,
            collaborative docs, and campus professional network.
          </p>
          <div className="mt-4 grid md:grid-cols-2 gap-3">
            {projectLinks.map((item) => (
              <div key={item.name} className="rounded-xl bg-slate-800 border border-slate-700 p-3">
                <p className="font-semibold">{item.name}</p>
                <div className="text-sm mt-2 flex gap-3">
                  {item.github ? (
                    <a href={item.github} target="_blank" rel="noreferrer" className="text-cyan-300 hover:text-cyan-200">GitHub</a>
                  ) : (
                    <span className="text-slate-500">GitHub: set NEXT_PUBLIC_*_GITHUB</span>
                  )}
                  {item.live ? (
                    <a href={item.live} target="_blank" rel="noreferrer" className="text-emerald-300 hover:text-emerald-200">Vercel Live</a>
                  ) : (
                    <span className="text-slate-500">Live: set NEXT_PUBLIC_*_LIVE</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section className="grid lg:grid-cols-2 gap-6">
          <article className="rounded-2xl border border-slate-700 bg-slate-900 p-5 space-y-3">
            <h2 className="text-xl font-bold">1) Twitter Clone (Real-time Posts)</h2>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2"
                value={tweetText}
                onChange={(e) => setTweetText(e.target.value)}
                placeholder="Share what you are building..."
              />
              <button
                className="px-4 rounded-lg bg-cyan-600 hover:bg-cyan-500"
                onClick={async () => {
                  if (!tweetText.trim()) return;
                  await fetch("/api/mvp/twitter", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: tweetText, author: "you" }),
                  });
                  setTweetText("");
                  loadTweets();
                }}
              >
                Post
              </button>
            </div>
            <div className="space-y-2 max-h-56 overflow-auto">
              {tweets.map((tweet) => (
                <div key={tweet.id} className="rounded-lg bg-slate-800 p-3">
                  <p className="text-sm text-slate-400">@{tweet.author}</p>
                  <p>{tweet.text}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="rounded-2xl border border-slate-700 bg-slate-900 p-5 space-y-3">
            <h2 className="text-xl font-bold">2) Instagram Reels + UPI Tips</h2>
            <div className="grid grid-cols-3 gap-2">
              {reels.map((reel) => (
                <div key={reel.id} className="rounded-lg p-3 bg-gradient-to-br from-rose-500/40 to-orange-500/30 border border-rose-400/30">
                  <p className="text-xs text-rose-100">{reel.creator}</p>
                  <p className="text-sm mt-2">{reel.title}</p>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input
                className="w-1/2 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2"
                value={tipCreator}
                onChange={(e) => setTipCreator(e.target.value)}
                placeholder="Creator handle"
              />
              <input
                type="number"
                className="w-1/4 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2"
                value={tipAmount}
                onChange={(e) => setTipAmount(Number(e.target.value))}
              />
              <button
                className="px-4 rounded-lg bg-emerald-600 hover:bg-emerald-500"
                onClick={async () => {
                  await fetch("/api/mvp/reels-tip", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ creator: tipCreator, amount: tipAmount }),
                  });
                  loadTips();
                }}
              >
                Tip
              </button>
            </div>
            <div className="space-y-1 text-sm max-h-28 overflow-auto">
              {tips.map((tip) => (
                <p key={tip.id} className="text-slate-300">
                  INR {tip.amount} to {tip.creator} via {tip.upiId}
                </p>
              ))}
            </div>
          </article>

          <article className="rounded-2xl border border-slate-700 bg-slate-900 p-5 space-y-3">
            <h2 className="text-xl font-bold">3) Meesho-style Social Commerce</h2>
            <div className="space-y-2">
              {products.map((product) => (
                <div key={product.id} className="rounded-lg bg-slate-800 border border-slate-700 p-3 flex items-center justify-between">
                  <div>
                    <p className="font-medium">{product.name}</p>
                    <p className="text-sm text-slate-400">{product.seller}</p>
                  </div>
                  <div className="text-right">
                    <p>INR {product.price}</p>
                    <button
                      className="mt-1 text-sm px-2 py-1 rounded bg-sky-700 hover:bg-sky-600"
                      onClick={() => setCartCount((v) => v + 1)}
                    >
                      Add
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="rounded-lg bg-slate-800 p-3 text-sm">
              <p>Cart items: {cartCount}</p>
              <a href={upiCheckoutLink} className="text-emerald-300 hover:text-emerald-200">
                Checkout with UPI
              </a>
            </div>
          </article>

          <article className="rounded-2xl border border-slate-700 bg-slate-900 p-5 space-y-3">
            <h2 className="text-xl font-bold">4) Notion-style Collaborative Docs</h2>
            <textarea
              className="w-full h-40 bg-slate-800 border border-slate-700 rounded-lg p-3"
              value={sharedDoc}
              onChange={async (e) => {
                const value = e.target.value;
                setSharedDoc(value);
                await fetch("/api/mvp/docs", {
                  method: "PUT",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ content: value }),
                });
              }}
            />
            <p className="text-xs text-slate-400">Last sync: {docSavedAt || "-"}</p>
          </article>

          <article className="rounded-2xl border border-slate-700 bg-slate-900 p-5 space-y-3 lg:col-span-2">
            <h2 className="text-xl font-bold">5) LinkedIn Clone for GGSIPU Freshers</h2>
            <div className="flex gap-2">
              <input
                className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-3 py-2"
                placeholder="Share placement prep update"
                value={linkedinText}
                onChange={(e) => setLinkedinText(e.target.value)}
              />
              <button
                className="px-4 rounded-lg bg-indigo-600 hover:bg-indigo-500"
                onClick={async () => {
                  if (!linkedinText.trim()) return;
                  await fetch("/api/mvp/linkedin", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ text: linkedinText, author: "GGSIPU Student" }),
                  });
                  setLinkedinText("");
                  loadLinkedin();
                }}
              >
                Publish
              </button>
            </div>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="space-y-2 max-h-52 overflow-auto">
                {linkedinPosts.map((post) => (
                  <div key={post.id} className="rounded-lg bg-slate-800 p-3">
                    <p className="text-sm text-slate-400">{post.author}</p>
                    <p>{post.text}</p>
                  </div>
                ))}
              </div>
              <div className="space-y-2">
                {jobs.map((job) => (
                  <div key={job.id} className="rounded-lg bg-slate-800 p-3 border border-slate-700">
                    <p className="font-medium">{job.role}</p>
                    <p className="text-sm text-slate-400">{job.company}</p>
                    <p className="text-sm text-emerald-300">{job.stipend}</p>
                  </div>
                ))}
              </div>
            </div>
          </article>
        </section>
      </div>
    </main>
  );
}
