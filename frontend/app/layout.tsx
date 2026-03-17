/**
 * Root Layout for Agentic CodeForge Dashboard
 */

import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agentic CodeForge | AI-Powered Full-Stack Code Generator",
  description: "Build production-ready full-stack apps in minutes. Describe your app in plain English, and our AI agents generate, validate, and deploy complete codebases.",
  keywords: ["AI", "code generation", "full-stack", "Next.js", "TinyFish", "hackathon"],
  authors: [{ name: "CodeForge Team" }],
  openGraph: {
    title: "Agentic CodeForge",
    description: "Build full-stack apps in minutes with AI",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Agentic CodeForge",
    description: "Build full-stack apps in minutes with AI",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className={inter.className}>
        {children}
      </body>
    </html>
  );
}
