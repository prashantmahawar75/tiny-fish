/**
 * Agentic CodeForge Dashboard
 * Main page with SSE streaming for real-time progress
 */

"use client";

import { useState, useRef, useEffect } from "react";
import { Loader2, Sparkles, Github, ExternalLink, Copy, Check, Rocket, Code, Database, Cloud, FileCode, Zap } from "lucide-react";

interface GenerationProgress {
  phase: string;
  progress: number;
  message: string;
  timestamp: string;
  status?: string;
  repo_url?: string;
  live_url?: string;
  metrics?: {
    total_files: number;
    total_lines: number;
    lighthouse_score: number;
    generation_time_seconds: number;
    agents_used: number;
  };
}

const phaseIcons: Record<string, React.ReactNode> = {
  init: <Sparkles className="w-5 h-5" />,
  swarm: <Code className="w-5 h-5" />,
  synthesis: <Zap className="w-5 h-5" />,
  generation: <FileCode className="w-5 h-5" />,
  validation: <Database className="w-5 h-5" />,
  deploy: <Cloud className="w-5 h-5" />,
  complete: <Rocket className="w-5 h-5" />,
  error: <Loader2 className="w-5 h-5" />,
};

const exampleSpecs = [
  "Twitter clone with real-time posts, Hindi support, and dark mode",
  "Instagram Reels clone with UPI creator tips for Indian audiences",
  "Meesho-style social commerce platform with UPI and COD payments",
  "Notion-style collaborative docs with real-time editing",
  "LinkedIn clone for GGSIPU freshers with job recommendations",
];

export default function Dashboard() {
  const [spec, setSpec] = useState("");
  const [email, setEmail] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState<GenerationProgress[]>([]);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [finalResult, setFinalResult] = useState<GenerationProgress | null>(null);
  const [copied, setCopied] = useState(false);
  const progressRef = useRef<HTMLDivElement>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || "https://backend-29vujjht3-prashants-projects-6a7a6282.vercel.app";

  const handleGenerate = async () => {
    if (!spec.trim() || !email.trim()) return;

    setIsGenerating(true);
    setProgress([]);
    setCurrentProgress(0);
    setFinalResult(null);

    try {
      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          spec: spec.trim(),
          user_email: email.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error("No response body");
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split("\n\n").filter((line) => line.trim());

        for (const line of lines) {
          try {
            const data = JSON.parse(line) as GenerationProgress;
            setProgress((prev) => [...prev, data]);
            setCurrentProgress(data.progress);

            if (data.phase === "complete" || data.phase === "error") {
              setFinalResult(data);
            }
          } catch (e) {
            console.log("Failed to parse:", line);
          }
        }
      }
    } catch (error) {
      console.error("Generation error:", error);
      setProgress((prev) => [
        ...prev,
        {
          phase: "error",
          progress: -1,
          message: `Error: ${error instanceof Error ? error.message : "Unknown error"}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setIsGenerating(false);
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  useEffect(() => {
    if (progressRef.current) {
      progressRef.current.scrollTop = progressRef.current.scrollHeight;
    }
  }, [progress]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Agentic CodeForge</h1>
                <p className="text-xs text-slate-400">TinyFish Hackathon</p>
              </div>
            </div>
            <a
              href="https://github.com/codeforge"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-700/50 hover:bg-slate-700 transition-colors text-white"
            >
              <Github className="w-4 h-4" />
              <span className="text-sm">GitHub</span>
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <h2 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
              Build Full-Stack Apps in Minutes
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              Describe your app in plain English. Our AI agents extract patterns from live websites
              and generate production-ready code deployed to Vercel.
            </p>
            <a
              href="/mvp"
              className="inline-flex items-center px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-sm font-medium transition-colors"
            >
              Open 5 Hardcoded MVP Clones
            </a>
          </div>

          {/* Input Section */}
          <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                App Specification
              </label>
              <textarea
                value={spec}
                onChange={(e) => setSpec(e.target.value)}
                placeholder="Describe your app... e.g., 'Twitter clone with real-time posts and Hindi support'"
                className="w-full h-32 px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                disabled={isGenerating}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Your Email
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                className="w-full px-4 py-3 rounded-xl bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isGenerating}
              />
            </div>

            {/* Example Specs */}
            <div className="space-y-2">
              <p className="text-xs text-slate-500">Try an example:</p>
              <div className="flex flex-wrap gap-2">
                {exampleSpecs.map((example, i) => (
                  <button
                    key={i}
                    onClick={() => setSpec(example)}
                    className="px-3 py-1.5 text-xs rounded-full bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition-colors"
                    disabled={isGenerating}
                  >
                    {example.slice(0, 30)}...
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleGenerate}
              disabled={isGenerating || !spec.trim() || !email.trim()}
              className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold text-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Rocket className="w-5 h-5" />
                  Generate Full-Stack App
                </>
              )}
            </button>
          </div>

          {/* Progress Section */}
          {progress.length > 0 && (
            <div className="bg-slate-800/50 rounded-2xl border border-slate-700/50 p-6 space-y-4">
              {/* Progress Bar */}
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-slate-400">Progress</span>
                  <span className="text-white font-medium">{Math.max(0, currentProgress)}%</span>
                </div>
                <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-500 ease-out"
                    style={{ width: `${Math.max(0, currentProgress)}%` }}
                  />
                </div>
              </div>

              {/* Progress Log */}
              <div
                ref={progressRef}
                className="max-h-64 overflow-y-auto space-y-2 font-mono text-sm"
              >
                {progress.map((item, i) => (
                  <div
                    key={i}
                    className={`flex items-start gap-3 p-3 rounded-lg ${
                      item.phase === "error"
                        ? "bg-red-900/20 border border-red-800/50"
                        : item.phase === "complete"
                        ? "bg-green-900/20 border border-green-800/50"
                        : "bg-slate-700/30"
                    }`}
                  >
                    <div
                      className={`mt-0.5 ${
                        item.phase === "error"
                          ? "text-red-400"
                          : item.phase === "complete"
                          ? "text-green-400"
                          : "text-blue-400"
                      }`}
                    >
                      {phaseIcons[item.phase] || phaseIcons.init}
                    </div>
                    <div className="flex-1">
                      <p
                        className={
                          item.phase === "error"
                            ? "text-red-300"
                            : item.phase === "complete"
                            ? "text-green-300"
                            : "text-slate-300"
                        }
                      >
                        {item.message}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        {new Date(item.timestamp).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Final Result */}
          {finalResult && finalResult.status === "success" && (
            <div className="bg-gradient-to-br from-green-900/30 to-blue-900/30 rounded-2xl border border-green-700/50 p-6 space-y-6">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                  <Check className="w-6 h-6 text-green-400" />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Generation Complete!</h3>
                  <p className="text-green-400">Your app is live and ready</p>
                </div>
              </div>

              {/* Links */}
              <div className="grid md:grid-cols-2 gap-4">
                <a
                  href={finalResult.live_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-blue-500 transition-colors group"
                >
                  <ExternalLink className="w-5 h-5 text-blue-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-400">Live Demo</p>
                    <p className="text-white truncate group-hover:text-blue-400 transition-colors">
                      {finalResult.live_url}
                    </p>
                  </div>
                </a>

                <a
                  href={finalResult.repo_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-3 p-4 rounded-xl bg-slate-800/50 border border-slate-700 hover:border-purple-500 transition-colors group"
                >
                  <Github className="w-5 h-5 text-purple-400" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-slate-400">GitHub Repository</p>
                    <p className="text-white truncate group-hover:text-purple-400 transition-colors">
                      {finalResult.repo_url}
                    </p>
                  </div>
                </a>
              </div>

              {/* Metrics */}
              {finalResult.metrics && (
                <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                  <div className="p-4 rounded-xl bg-slate-800/50 text-center">
                    <p className="text-2xl font-bold text-white">{finalResult.metrics.total_files}</p>
                    <p className="text-xs text-slate-400">Files</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-800/50 text-center">
                    <p className="text-2xl font-bold text-white">{finalResult.metrics.total_lines.toLocaleString()}</p>
                    <p className="text-xs text-slate-400">Lines</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-800/50 text-center">
                    <p className="text-2xl font-bold text-green-400">{finalResult.metrics.lighthouse_score}</p>
                    <p className="text-xs text-slate-400">Lighthouse</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-800/50 text-center">
                    <p className="text-2xl font-bold text-white">{finalResult.metrics.generation_time_seconds}s</p>
                    <p className="text-xs text-slate-400">Time</p>
                  </div>
                  <div className="p-4 rounded-xl bg-slate-800/50 text-center">
                    <p className="text-2xl font-bold text-blue-400">{finalResult.metrics.agents_used}</p>
                    <p className="text-xs text-slate-400">Agents</p>
                  </div>
                </div>
              )}

              {/* Copy URLs */}
              <div className="flex gap-2">
                <button
                  onClick={() => copyToClipboard(`${finalResult.live_url}`)}
                  className="flex-1 py-3 rounded-xl bg-slate-700/50 hover:bg-slate-700 text-white font-medium transition-colors flex items-center justify-center gap-2"
                >
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                  Copy Live URL
                </button>
                <button
                  onClick={() =>
                    window.open(
                      `https://twitter.com/intent/tweet?text=${encodeURIComponent(
                        `🚀 Just built "${spec.slice(0, 50)}..." in minutes with @Tiny_fish CodeForge!\n\n${finalResult.live_url}`
                      )}`,
                      "_blank"
                    )
                  }
                  className="px-6 py-3 rounded-xl bg-blue-500 hover:bg-blue-600 text-white font-medium transition-colors"
                >
                  Share on X
                </button>
              </div>
            </div>
          )}

          {/* Tech Stack */}
          <div className="text-center space-y-4 pt-8">
            <p className="text-sm text-slate-500">Powered by</p>
            <div className="flex flex-wrap justify-center gap-4 text-xs text-slate-400">
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">TinyFish Agents</span>
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">Fireworks.ai</span>
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">Next.js 15</span>
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">Supabase</span>
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">Vercel</span>
              <span className="px-3 py-1.5 rounded-full bg-slate-800/50 border border-slate-700">Composio</span>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-700/50 mt-16">
        <div className="container mx-auto px-4 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-slate-500">
              Built for TinyFish Hackathon 2024 | Golden Ticket Competition
            </p>
            <div className="flex items-center gap-4">
              <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors">
                Documentation
              </a>
              <a href="#" className="text-sm text-slate-400 hover:text-white transition-colors">
                API
              </a>
              <a href="https://github.com/codeforge" className="text-sm text-slate-400 hover:text-white transition-colors">
                GitHub
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
