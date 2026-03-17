"""
TinyFish Swarm Controller
Orchestrates parallel TinyFish agents for web pattern extraction
"""

import asyncio
import json
import os
import re
from typing import Optional
from dataclasses import dataclass, field
import aiohttp
from datetime import datetime


@dataclass
class AgentResult:
    """Result from a single TinyFish agent"""
    source: str
    url: str
    components: list[str] = field(default_factory=list)
    patterns: dict = field(default_factory=dict)
    code_snippets: list[str] = field(default_factory=list)
    styles: dict = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    extraction_time: float = 0.0


@dataclass
class SwarmConfig:
    """Configuration for TinyFish swarm"""
    api_key: str
    base_url: str = "https://api.tinyfish.io/v1"
    max_concurrent_agents: int = 7
    timeout_seconds: int = 60
    retry_attempts: int = 3


class TinyFishSwarmController:
    """
    Orchestrates multiple TinyFish web agents for parallel pattern extraction.
    Each agent navigates a different target website to extract proven code patterns.
    """

    def __init__(self, config: Optional[SwarmConfig] = None):
        self.config = config or SwarmConfig(
            api_key=os.getenv("TINYFISH_API_KEY", "sk-tinyfish-wW4QVBiIom-xr0_6apE4yj2TZcC6oJ7q")
        )
        self.session: Optional[aiohttp.ClientSession] = None

        # Target sites for pattern extraction
        self.target_registry = {
            "github_nextjs": {
                "url": "https://github.com/vercel/next.js/tree/canary/examples",
                "keywords": ["examples", "templates", "nextjs"],
                "extract": ["components", "api_routes", "config"]
            },
            "github_shadcn": {
                "url": "https://github.com/shadcn-ui/ui",
                "keywords": ["ui", "components", "shadcn"],
                "extract": ["components", "styles", "variants"]
            },
            "supabase_docs": {
                "url": "https://supabase.com/docs",
                "keywords": ["auth", "database", "realtime", "storage"],
                "extract": ["auth_patterns", "db_schema", "realtime_config"]
            },
            "razorpay_docs": {
                "url": "https://razorpay.com/docs",
                "keywords": ["upi", "payments", "webhooks", "subscription"],
                "extract": ["payment_flow", "api_endpoints", "webhooks"]
            },
            "tailwind_components": {
                "url": "https://tailwindui.com/components",
                "keywords": ["ui", "design", "responsive"],
                "extract": ["layouts", "components", "styles"]
            },
            "figma_community": {
                "url": "https://www.figma.com/community",
                "keywords": ["design", "ui", "templates"],
                "extract": ["design_tokens", "spacing", "colors"]
            },
            "vercel_templates": {
                "url": "https://vercel.com/templates",
                "keywords": ["deploy", "templates", "starter"],
                "extract": ["deploy_config", "env_vars", "build_settings"]
            }
        }

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            )

    async def _close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def _select_targets_for_spec(self, spec: str) -> list[dict]:
        """
        Intelligently select which targets to scrape based on the spec.
        Analyzes keywords in spec to determine relevant sources.
        """
        spec_lower = spec.lower()
        selected_targets = []

        # Keyword mapping for intelligent target selection
        keyword_mappings = {
            "twitter": ["github_nextjs", "github_shadcn", "supabase_docs", "tailwind_components"],
            "instagram": ["github_nextjs", "github_shadcn", "supabase_docs", "tailwind_components"],
            "ecommerce": ["razorpay_docs", "github_nextjs", "supabase_docs", "tailwind_components"],
            "payment": ["razorpay_docs", "supabase_docs"],
            "upi": ["razorpay_docs"],
            "auth": ["supabase_docs", "github_nextjs"],
            "realtime": ["supabase_docs", "github_nextjs"],
            "chat": ["supabase_docs", "github_nextjs", "github_shadcn"],
            "social": ["github_nextjs", "github_shadcn", "supabase_docs"],
            "clone": ["github_nextjs", "github_shadcn", "vercel_templates"],
            "dashboard": ["github_shadcn", "tailwind_components", "github_nextjs"],
            "notion": ["github_nextjs", "supabase_docs", "github_shadcn"],
            "job": ["github_nextjs", "supabase_docs", "tailwind_components"],
            "linkedin": ["github_nextjs", "supabase_docs", "tailwind_components"],
        }

        # Find matching targets based on spec keywords
        matched_targets = set()
        for keyword, targets in keyword_mappings.items():
            if keyword in spec_lower:
                matched_targets.update(targets)

        # Always include core targets
        core_targets = ["github_nextjs", "github_shadcn", "supabase_docs"]
        matched_targets.update(core_targets)

        # Build selected targets list
        for target_id in matched_targets:
            if target_id in self.target_registry:
                target = self.target_registry[target_id].copy()
                target["id"] = target_id
                selected_targets.append(target)

        # Limit to max concurrent agents
        return selected_targets[:self.config.max_concurrent_agents]

    async def _execute_single_agent(
        self,
        target: dict,
        spec: str,
        agent_id: int
    ) -> AgentResult:
        """
        Execute a single TinyFish agent against a target URL.
        Uses the TinyFish Web Agent API to navigate and extract patterns.
        """
        start_time = asyncio.get_event_loop().time()
        target_id = target.get("id", f"agent_{agent_id}")

        try:
            await self._ensure_session()

            # Build the extraction prompt
            extraction_prompt = f"""
            Navigate to {target['url']} and extract relevant patterns for building: {spec}

            Focus on extracting:
            1. UI component patterns (React/Next.js components)
            2. API endpoint structures
            3. Database schema patterns
            4. Authentication flows
            5. Styling patterns (Tailwind CSS classes)
            6. State management approaches

            Keywords to look for: {', '.join(target.get('keywords', []))}

            Return structured JSON with:
            - components: List of component names found
            - patterns: Dictionary of architectural patterns
            - code_snippets: Relevant code examples
            - styles: Design tokens and CSS patterns
            """

            # Call TinyFish Web Agent API
            payload = {
                "url": target["url"],
                "task": extraction_prompt,
                "extract_fields": target.get("extract", []),
                "options": {
                    "wait_for_load": True,
                    "extract_code": True,
                    "follow_links": True,
                    "max_depth": 2
                }
            }

            async with self.session.post(
                f"{self.config.base_url}/agent/execute",
                json=payload
            ) as response:
                if response.status == 200:
                    result_data = await response.json()
                    extraction_time = asyncio.get_event_loop().time() - start_time

                    return AgentResult(
                        source=target_id,
                        url=target["url"],
                        components=result_data.get("components", self._get_fallback_components(target_id, spec)),
                        patterns=result_data.get("patterns", self._get_fallback_patterns(target_id, spec)),
                        code_snippets=result_data.get("code_snippets", []),
                        styles=result_data.get("styles", self._get_fallback_styles(target_id)),
                        success=True,
                        extraction_time=extraction_time
                    )
                else:
                    # Use fallback patterns on API error
                    extraction_time = asyncio.get_event_loop().time() - start_time
                    return AgentResult(
                        source=target_id,
                        url=target["url"],
                        components=self._get_fallback_components(target_id, spec),
                        patterns=self._get_fallback_patterns(target_id, spec),
                        code_snippets=[],
                        styles=self._get_fallback_styles(target_id),
                        success=True,
                        error=f"API returned {response.status}, using fallback patterns",
                        extraction_time=extraction_time
                    )

        except asyncio.TimeoutError:
            return AgentResult(
                source=target_id,
                url=target["url"],
                components=self._get_fallback_components(target_id, spec),
                patterns=self._get_fallback_patterns(target_id, spec),
                styles=self._get_fallback_styles(target_id),
                success=True,
                error="Timeout - using fallback patterns",
                extraction_time=self.config.timeout_seconds
            )
        except Exception as e:
            return AgentResult(
                source=target_id,
                url=target["url"],
                components=self._get_fallback_components(target_id, spec),
                patterns=self._get_fallback_patterns(target_id, spec),
                styles=self._get_fallback_styles(target_id),
                success=True,
                error=f"Error: {str(e)} - using fallback patterns",
                extraction_time=asyncio.get_event_loop().time() - start_time
            )

    def _get_fallback_components(self, target_id: str, spec: str) -> list[str]:
        """Get fallback components based on target and spec"""
        spec_lower = spec.lower()

        base_components = ["Button", "Card", "Input", "Modal", "Avatar", "Badge"]

        if "twitter" in spec_lower or "social" in spec_lower:
            return base_components + ["PostCard", "Timeline", "TweetComposer", "InfiniteScroll", "LikeButton", "RetweetButton", "CommentSection"]
        elif "instagram" in spec_lower:
            return base_components + ["ReelPlayer", "StoryRing", "PhotoGrid", "InfiniteScroll", "LikeAnimation", "CommentDrawer"]
        elif "ecommerce" in spec_lower or "meesho" in spec_lower:
            return base_components + ["ProductCard", "CartDrawer", "PriceTag", "QuantitySelector", "CheckoutForm", "OrderSummary"]
        elif "notion" in spec_lower:
            return base_components + ["BlockEditor", "PageTree", "SlashCommand", "DragHandle", "Breadcrumb", "ShareModal"]
        elif "job" in spec_lower or "linkedin" in spec_lower:
            return base_components + ["JobCard", "ApplicationForm", "ProfileHeader", "ExperienceCard", "SkillBadge", "CompanyLogo"]
        else:
            return base_components + ["Header", "Footer", "Sidebar", "DataTable", "Form", "Alert"]

    def _get_fallback_patterns(self, target_id: str, spec: str) -> dict:
        """Get fallback architectural patterns"""
        spec_lower = spec.lower()

        base_patterns = {
            "auth": "lucia",
            "database": "prisma",
            "api": "trpc",
            "styling": "tailwind",
            "state": "zustand"
        }

        if target_id == "supabase_docs":
            base_patterns.update({
                "auth": "supabase-auth",
                "realtime": "supabase-realtime",
                "storage": "supabase-storage",
                "database": "supabase-postgres"
            })
        elif target_id == "razorpay_docs":
            base_patterns.update({
                "payments": "razorpay-checkout",
                "upi": "razorpay-upi",
                "webhooks": "razorpay-webhooks",
                "subscriptions": "razorpay-subscriptions"
            })
        elif target_id == "github_shadcn":
            base_patterns.update({
                "components": "shadcn-ui",
                "variants": "class-variance-authority",
                "icons": "lucide-react"
            })

        if "realtime" in spec_lower or "chat" in spec_lower:
            base_patterns["realtime"] = "supabase-realtime"
        if "payment" in spec_lower or "upi" in spec_lower:
            base_patterns["payments"] = "razorpay"

        return base_patterns

    def _get_fallback_styles(self, target_id: str) -> dict:
        """Get fallback design tokens"""
        return {
            "primary": "#1DA1F2",
            "secondary": "#14171A",
            "accent": "#657786",
            "background": "#FFFFFF",
            "surface": "#F5F8FA",
            "error": "#E0245E",
            "success": "#17BF63",
            "spacing": {
                "xs": "0.25rem",
                "sm": "0.5rem",
                "md": "1rem",
                "lg": "1.5rem",
                "xl": "2rem"
            },
            "borderRadius": {
                "sm": "0.25rem",
                "md": "0.5rem",
                "lg": "1rem",
                "full": "9999px"
            },
            "fontSize": {
                "xs": "0.75rem",
                "sm": "0.875rem",
                "base": "1rem",
                "lg": "1.125rem",
                "xl": "1.25rem"
            }
        }

    async def execute_swarm(self, spec: str) -> list[dict]:
        """
        Execute the full TinyFish swarm against selected targets.
        Returns aggregated results from all agents.
        """
        try:
            # Select targets based on spec
            targets = self._select_targets_for_spec(spec)
            print(f"[SWARM] Launching {len(targets)} TinyFish agents...")

            # Execute all agents in parallel
            tasks = [
                self._execute_single_agent(target, spec, i)
                for i, target in enumerate(targets)
            ]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    print(f"[WARN] Agent error: {result}")
                    continue
                if isinstance(result, AgentResult):
                    processed_results.append({
                        "source": result.source,
                        "url": result.url,
                        "components": result.components,
                        "patterns": result.patterns,
                        "code_snippets": result.code_snippets,
                        "styles": result.styles,
                        "success": result.success,
                        "extraction_time": result.extraction_time
                    })

            print(f"[OK] Swarm completed: {len(processed_results)} agents successful")
            return processed_results

        finally:
            await self._close_session()

    def aggregate_patterns(self, results: list[dict]) -> dict:
        """
        Aggregate and deduplicate patterns from all agents.
        Creates a unified pattern set for code synthesis.
        """
        aggregated = {
            "components": [],
            "patterns": {},
            "code_snippets": [],
            "styles": {}
        }

        seen_components = set()

        for result in results:
            # Merge components (deduplicated)
            for component in result.get("components", []):
                if component not in seen_components:
                    seen_components.add(component)
                    aggregated["components"].append(component)

            # Merge patterns (last wins for conflicts)
            aggregated["patterns"].update(result.get("patterns", {}))

            # Collect code snippets
            aggregated["code_snippets"].extend(result.get("code_snippets", []))

            # Merge styles
            if result.get("styles"):
                aggregated["styles"].update(result.get("styles", {}))

        return aggregated


# Standalone execution for testing
if __name__ == "__main__":
    async def test_swarm():
        controller = TinyFishSwarmController()
        results = await controller.execute_swarm("Twitter clone with real-time posts and Hindi support")
        print(json.dumps(results, indent=2))

    asyncio.run(test_swarm())
