"""
Code Synthesis Engine
Uses Fireworks.ai (Llama 3.2) to synthesize patterns into code blueprints
"""

import asyncio
import json
import os
import re
from typing import Optional
from dataclasses import dataclass
import aiohttp


@dataclass
class SynthesisConfig:
    """Configuration for Fireworks.ai synthesis"""
    api_key: str
    base_url: str = "https://api.fireworks.ai/inference/v1"
    model: str = "accounts/fireworks/models/llama-v3p2-3b-instruct"
    fallback_model: str = "accounts/fireworks/models/llama-v3p1-8b-instruct"
    max_tokens: int = 4096
    temperature: float = 0.7


class CodeSynthesisEngine:
    """
    Synthesizes extracted patterns into unified code blueprints.
    Uses Fireworks.ai Llama 3.2 for intelligent code generation.
    """

    def __init__(self, config: Optional[SynthesisConfig] = None):
        self.config = config or SynthesisConfig(
            api_key=os.getenv("FIREWORKS_API_KEY", "")
        )
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=120)
            )

    async def _close_session(self):
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    def _build_synthesis_prompt(self, spec: str, swarm_results: list[dict]) -> str:
        """Build the prompt for synthesis"""

        # Aggregate all components and patterns
        all_components = []
        all_patterns = {}
        all_styles = {}

        for result in swarm_results:
            all_components.extend(result.get("components", []))
            all_patterns.update(result.get("patterns", {}))
            all_styles.update(result.get("styles", {}))

        # Deduplicate components
        unique_components = list(set(all_components))

        prompt = f"""You are an expert full-stack architect. Analyze the following extracted patterns and create a complete code blueprint.

## User Specification
{spec}

## Extracted Components (from live websites)
{json.dumps(unique_components, indent=2)}

## Extracted Patterns
{json.dumps(all_patterns, indent=2)}

## Design Tokens
{json.dumps(all_styles, indent=2)}

## Your Task
Create a comprehensive code blueprint in JSON format with:

1. **ui_components**: Array of component definitions with:
   - name: Component name
   - type: "page" | "layout" | "component" | "feature"
   - shadcn_base: The shadcn/ui component to extend
   - props: Array of prop definitions
   - description: What the component does

2. **api_endpoints**: Array of tRPC router definitions with:
   - name: Endpoint name
   - method: "query" | "mutation"
   - input_schema: Zod schema definition
   - description: What the endpoint does
   - auth_required: boolean

3. **database_tables**: Array of Prisma schema definitions with:
   - name: Table name
   - fields: Array of field definitions
   - relations: Array of relation definitions

4. **auth_config**: Authentication configuration with:
   - provider: "supabase" | "lucia" | "next-auth"
   - strategies: Array of auth strategies
   - protected_routes: Array of protected route patterns

5. **deployment_config**: Deployment settings with:
   - platform: "vercel"
   - env_vars: Required environment variables
   - build_command: Build command
   - output_directory: Output directory

6. **summary**: One-line summary of the generated blueprint

Return ONLY valid JSON, no markdown code blocks or explanation."""

        return prompt

    async def _call_fireworks_api(self, prompt: str, use_fallback: bool = False) -> dict:
        """Call Fireworks.ai API"""
        await self._ensure_session()

        model = self.config.fallback_model if use_fallback else self.config.model

        payload = {
            "model": model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert code architect. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "response_format": {"type": "json_object"}
        }

        try:
            async with self.session.post(
                f"{self.config.base_url}/chat/completions",
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result["choices"][0]["message"]["content"]
                    return json.loads(content)
                else:
                    error_text = await response.text()
                    raise Exception(f"Fireworks API error: {response.status} - {error_text}")

        except json.JSONDecodeError as e:
            if not use_fallback:
                print("[WARN] JSON parse error, trying fallback model...")
                return await self._call_fireworks_api(prompt, use_fallback=True)
            raise e

    def _generate_fallback_blueprint(self, spec: str, swarm_results: list[dict]) -> dict:
        """Generate fallback blueprint when API fails"""

        spec_lower = spec.lower()

        # Determine app type from spec
        if "twitter" in spec_lower:
            app_type = "twitter_clone"
        elif "instagram" in spec_lower:
            app_type = "instagram_clone"
        elif "ecommerce" in spec_lower or "meesho" in spec_lower:
            app_type = "ecommerce"
        elif "notion" in spec_lower:
            app_type = "notion_clone"
        elif "job" in spec_lower or "linkedin" in spec_lower:
            app_type = "job_board"
        else:
            app_type = "social_app"

        # Aggregate components from swarm
        all_components = []
        for result in swarm_results:
            all_components.extend(result.get("components", []))
        unique_components = list(set(all_components))

        # Build blueprint based on app type
        blueprints = {
            "twitter_clone": self._twitter_blueprint(unique_components),
            "instagram_clone": self._instagram_blueprint(unique_components),
            "ecommerce": self._ecommerce_blueprint(unique_components),
            "notion_clone": self._notion_blueprint(unique_components),
            "job_board": self._job_board_blueprint(unique_components),
            "social_app": self._social_app_blueprint(unique_components)
        }

        blueprint = blueprints.get(app_type, blueprints["social_app"])

        # Add Hindi support if mentioned
        if "hindi" in spec_lower or "india" in spec_lower:
            blueprint["i18n"] = {
                "default_locale": "en",
                "locales": ["en", "hi"],
                "setup": "next-intl"
            }

        # Add payment support if mentioned
        if "upi" in spec_lower or "payment" in spec_lower:
            blueprint["payments"] = {
                "provider": "razorpay",
                "methods": ["upi", "card", "netbanking"],
                "currency": "INR"
            }

        blueprint["summary"] = f"Full-stack {app_type.replace('_', ' ')} with {len(blueprint['ui_components'])} components and {len(blueprint['api_endpoints'])} API endpoints"

        return blueprint

    def _twitter_blueprint(self, components: list[str]) -> dict:
        """Twitter clone blueprint"""
        return {
            "ui_components": [
                {"name": "Timeline", "type": "page", "shadcn_base": "ScrollArea", "props": ["posts", "onLoadMore"], "description": "Infinite scrolling timeline"},
                {"name": "PostCard", "type": "component", "shadcn_base": "Card", "props": ["post", "onLike", "onRetweet"], "description": "Single post display"},
                {"name": "TweetComposer", "type": "feature", "shadcn_base": "Dialog", "props": ["onSubmit", "maxLength"], "description": "Create new tweets"},
                {"name": "UserProfile", "type": "page", "shadcn_base": "Card", "props": ["user", "isOwnProfile"], "description": "User profile page"},
                {"name": "Sidebar", "type": "layout", "shadcn_base": "NavigationMenu", "props": ["user", "unreadCount"], "description": "Navigation sidebar"},
                {"name": "TrendingTopics", "type": "component", "shadcn_base": "Card", "props": ["topics"], "description": "Trending hashtags"},
                {"name": "SearchBar", "type": "component", "shadcn_base": "Input", "props": ["onSearch", "placeholder"], "description": "Global search"},
                {"name": "NotificationBell", "type": "component", "shadcn_base": "DropdownMenu", "props": ["notifications"], "description": "Notification dropdown"},
                {"name": "FollowButton", "type": "component", "shadcn_base": "Button", "props": ["userId", "isFollowing"], "description": "Follow/unfollow toggle"},
                {"name": "LikeButton", "type": "component", "shadcn_base": "Button", "props": ["postId", "isLiked", "count"], "description": "Like toggle with animation"},
                {"name": "ReplyThread", "type": "feature", "shadcn_base": "ScrollArea", "props": ["postId", "replies"], "description": "Threaded replies"},
                {"name": "MediaUploader", "type": "component", "shadcn_base": "Input", "props": ["onUpload", "maxFiles"], "description": "Image/video uploader"}
            ],
            "api_endpoints": [
                {"name": "posts.timeline", "method": "query", "input_schema": "{ cursor?: string, limit?: number }", "description": "Get paginated timeline", "auth_required": True},
                {"name": "posts.create", "method": "mutation", "input_schema": "{ content: string, mediaUrls?: string[] }", "description": "Create new post", "auth_required": True},
                {"name": "posts.like", "method": "mutation", "input_schema": "{ postId: string }", "description": "Like/unlike post", "auth_required": True},
                {"name": "posts.retweet", "method": "mutation", "input_schema": "{ postId: string }", "description": "Retweet post", "auth_required": True},
                {"name": "users.profile", "method": "query", "input_schema": "{ username: string }", "description": "Get user profile", "auth_required": False},
                {"name": "users.follow", "method": "mutation", "input_schema": "{ userId: string }", "description": "Follow/unfollow user", "auth_required": True},
                {"name": "search.posts", "method": "query", "input_schema": "{ query: string, cursor?: string }", "description": "Search posts", "auth_required": False},
                {"name": "notifications.list", "method": "query", "input_schema": "{ cursor?: string }", "description": "Get notifications", "auth_required": True}
            ],
            "database_tables": [
                {"name": "User", "fields": ["id String @id", "username String @unique", "email String @unique", "name String", "bio String?", "avatar String?", "createdAt DateTime"], "relations": ["posts Post[]", "likes Like[]", "followers Follow[]"]},
                {"name": "Post", "fields": ["id String @id", "content String", "authorId String", "mediaUrls String[]", "createdAt DateTime", "likesCount Int", "retweetsCount Int"], "relations": ["author User", "likes Like[]", "retweets Retweet[]"]},
                {"name": "Like", "fields": ["id String @id", "userId String", "postId String", "createdAt DateTime"], "relations": ["user User", "post Post"]},
                {"name": "Follow", "fields": ["id String @id", "followerId String", "followingId String", "createdAt DateTime"], "relations": ["follower User", "following User"]},
                {"name": "Notification", "fields": ["id String @id", "userId String", "type String", "actorId String", "postId String?", "read Boolean", "createdAt DateTime"], "relations": ["user User"]}
            ],
            "auth_config": {
                "provider": "supabase",
                "strategies": ["email", "google", "twitter"],
                "protected_routes": ["/home", "/compose", "/profile/*", "/notifications"]
            },
            "deployment_config": {
                "platform": "vercel",
                "env_vars": ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY", "NEXTAUTH_SECRET"],
                "build_command": "npm run build",
                "output_directory": ".next"
            }
        }

    def _instagram_blueprint(self, components: list[str]) -> dict:
        """Instagram clone blueprint"""
        return {
            "ui_components": [
                {"name": "Feed", "type": "page", "shadcn_base": "ScrollArea", "props": ["posts", "onLoadMore"], "description": "Photo feed"},
                {"name": "ReelPlayer", "type": "feature", "shadcn_base": "Card", "props": ["reel", "autoPlay"], "description": "Vertical video player"},
                {"name": "StoryRing", "type": "component", "shadcn_base": "Avatar", "props": ["stories", "hasUnviewed"], "description": "Story ring indicator"},
                {"name": "PhotoGrid", "type": "component", "shadcn_base": "Card", "props": ["photos", "columns"], "description": "Grid photo layout"},
                {"name": "PostCreator", "type": "feature", "shadcn_base": "Dialog", "props": ["onSubmit"], "description": "Create post modal"},
                {"name": "CommentDrawer", "type": "component", "shadcn_base": "Sheet", "props": ["postId", "comments"], "description": "Comments drawer"},
                {"name": "LikeAnimation", "type": "component", "shadcn_base": "Button", "props": ["isLiked"], "description": "Heart animation"},
                {"name": "ProfileHeader", "type": "component", "shadcn_base": "Card", "props": ["user", "stats"], "description": "Profile stats header"},
                {"name": "BottomNav", "type": "layout", "shadcn_base": "NavigationMenu", "props": ["currentPath"], "description": "Mobile bottom navigation"},
                {"name": "DirectMessages", "type": "page", "shadcn_base": "ScrollArea", "props": ["conversations"], "description": "DM inbox"},
                {"name": "ExploreGrid", "type": "page", "shadcn_base": "Card", "props": ["posts"], "description": "Explore page grid"},
                {"name": "FilterCarousel", "type": "component", "shadcn_base": "ScrollArea", "props": ["filters", "onSelect"], "description": "Photo filters"}
            ],
            "api_endpoints": [
                {"name": "posts.feed", "method": "query", "input_schema": "{ cursor?: string }", "description": "Get home feed", "auth_required": True},
                {"name": "posts.create", "method": "mutation", "input_schema": "{ mediaUrls: string[], caption?: string }", "description": "Create post", "auth_required": True},
                {"name": "reels.feed", "method": "query", "input_schema": "{ cursor?: string }", "description": "Get reels feed", "auth_required": True},
                {"name": "stories.get", "method": "query", "input_schema": "{ userId: string }", "description": "Get user stories", "auth_required": True},
                {"name": "comments.list", "method": "query", "input_schema": "{ postId: string }", "description": "Get post comments", "auth_required": False},
                {"name": "comments.create", "method": "mutation", "input_schema": "{ postId: string, content: string }", "description": "Add comment", "auth_required": True},
                {"name": "dm.send", "method": "mutation", "input_schema": "{ recipientId: string, content: string }", "description": "Send DM", "auth_required": True},
                {"name": "explore.search", "method": "query", "input_schema": "{ query: string }", "description": "Search explore", "auth_required": False}
            ],
            "database_tables": [
                {"name": "User", "fields": ["id String @id", "username String @unique", "email String @unique", "name String", "bio String?", "avatar String?", "isVerified Boolean"], "relations": ["posts Post[]", "stories Story[]"]},
                {"name": "Post", "fields": ["id String @id", "authorId String", "mediaUrls String[]", "caption String?", "likesCount Int", "commentsCount Int", "createdAt DateTime"], "relations": ["author User", "comments Comment[]"]},
                {"name": "Story", "fields": ["id String @id", "authorId String", "mediaUrl String", "expiresAt DateTime", "viewCount Int"], "relations": ["author User"]},
                {"name": "Reel", "fields": ["id String @id", "authorId String", "videoUrl String", "caption String?", "audioId String?", "viewCount Int"], "relations": ["author User"]},
                {"name": "Comment", "fields": ["id String @id", "postId String", "authorId String", "content String", "createdAt DateTime"], "relations": ["post Post", "author User"]}
            ],
            "auth_config": {
                "provider": "supabase",
                "strategies": ["email", "google", "facebook"],
                "protected_routes": ["/feed", "/create", "/profile/*", "/reels"]
            },
            "deployment_config": {
                "platform": "vercel",
                "env_vars": ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY", "CLOUDINARY_URL"],
                "build_command": "npm run build",
                "output_directory": ".next"
            }
        }

    def _ecommerce_blueprint(self, components: list[str]) -> dict:
        """Ecommerce blueprint"""
        return {
            "ui_components": [
                {"name": "ProductGrid", "type": "page", "shadcn_base": "Card", "props": ["products", "onLoadMore"], "description": "Product listing grid"},
                {"name": "ProductCard", "type": "component", "shadcn_base": "Card", "props": ["product", "onAddToCart"], "description": "Single product card"},
                {"name": "CartDrawer", "type": "feature", "shadcn_base": "Sheet", "props": ["items", "onCheckout"], "description": "Shopping cart drawer"},
                {"name": "CheckoutForm", "type": "page", "shadcn_base": "Form", "props": ["cart", "onSubmit"], "description": "Checkout form"},
                {"name": "PaymentModal", "type": "feature", "shadcn_base": "Dialog", "props": ["amount", "onSuccess"], "description": "Razorpay payment modal"},
                {"name": "CategoryNav", "type": "layout", "shadcn_base": "NavigationMenu", "props": ["categories"], "description": "Category navigation"},
                {"name": "SearchFilters", "type": "component", "shadcn_base": "Accordion", "props": ["filters", "onApply"], "description": "Product filters"},
                {"name": "PriceTag", "type": "component", "shadcn_base": "Badge", "props": ["price", "discount"], "description": "Price display"},
                {"name": "OrderSummary", "type": "component", "shadcn_base": "Card", "props": ["order"], "description": "Order summary card"},
                {"name": "AddressForm", "type": "component", "shadcn_base": "Form", "props": ["onSave"], "description": "Shipping address form"},
                {"name": "ReviewCard", "type": "component", "shadcn_base": "Card", "props": ["review"], "description": "Product review"},
                {"name": "WishlistButton", "type": "component", "shadcn_base": "Button", "props": ["productId", "isWishlisted"], "description": "Add to wishlist"}
            ],
            "api_endpoints": [
                {"name": "products.list", "method": "query", "input_schema": "{ category?: string, cursor?: string }", "description": "List products", "auth_required": False},
                {"name": "products.get", "method": "query", "input_schema": "{ productId: string }", "description": "Get product details", "auth_required": False},
                {"name": "cart.add", "method": "mutation", "input_schema": "{ productId: string, quantity: number }", "description": "Add to cart", "auth_required": True},
                {"name": "cart.get", "method": "query", "input_schema": "{}", "description": "Get cart", "auth_required": True},
                {"name": "orders.create", "method": "mutation", "input_schema": "{ addressId: string, paymentMethod: string }", "description": "Create order", "auth_required": True},
                {"name": "payments.createUpiLink", "method": "mutation", "input_schema": "{ orderId: string, amount: number }", "description": "Create Razorpay UPI link", "auth_required": True},
                {"name": "payments.verify", "method": "mutation", "input_schema": "{ paymentId: string, signature: string }", "description": "Verify payment", "auth_required": True},
                {"name": "orders.list", "method": "query", "input_schema": "{ cursor?: string }", "description": "List orders", "auth_required": True}
            ],
            "database_tables": [
                {"name": "User", "fields": ["id String @id", "email String @unique", "name String", "phone String?"], "relations": ["orders Order[]", "addresses Address[]", "cart CartItem[]"]},
                {"name": "Product", "fields": ["id String @id", "name String", "description String", "price Int", "discountPrice Int?", "images String[]", "categoryId String", "stock Int"], "relations": ["category Category"]},
                {"name": "Category", "fields": ["id String @id", "name String", "slug String @unique", "parentId String?"], "relations": ["products Product[]"]},
                {"name": "Order", "fields": ["id String @id", "userId String", "status String", "total Int", "addressId String", "paymentId String?"], "relations": ["user User", "items OrderItem[]"]},
                {"name": "CartItem", "fields": ["id String @id", "userId String", "productId String", "quantity Int"], "relations": ["user User", "product Product"]}
            ],
            "auth_config": {
                "provider": "supabase",
                "strategies": ["email", "phone", "google"],
                "protected_routes": ["/cart", "/checkout", "/orders/*", "/profile"]
            },
            "deployment_config": {
                "platform": "vercel",
                "env_vars": ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY", "RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET"],
                "build_command": "npm run build",
                "output_directory": ".next"
            }
        }

    def _notion_blueprint(self, components: list[str]) -> dict:
        """Notion clone blueprint"""
        return {
            "ui_components": [
                {"name": "BlockEditor", "type": "feature", "shadcn_base": "Card", "props": ["blocks", "onChange"], "description": "Rich text block editor"},
                {"name": "PageTree", "type": "component", "shadcn_base": "Accordion", "props": ["pages", "currentPageId"], "description": "Page hierarchy tree"},
                {"name": "SlashCommand", "type": "component", "shadcn_base": "Command", "props": ["onSelect"], "description": "Slash command menu"},
                {"name": "DragHandle", "type": "component", "shadcn_base": "Button", "props": ["blockId"], "description": "Block drag handle"},
                {"name": "Breadcrumb", "type": "component", "shadcn_base": "Breadcrumb", "props": ["path"], "description": "Page breadcrumb"},
                {"name": "ShareModal", "type": "feature", "shadcn_base": "Dialog", "props": ["pageId", "collaborators"], "description": "Share and permissions"},
                {"name": "TableBlock", "type": "component", "shadcn_base": "Table", "props": ["data", "columns"], "description": "Database table view"},
                {"name": "KanbanView", "type": "component", "shadcn_base": "Card", "props": ["items", "columns"], "description": "Kanban board view"},
                {"name": "CalendarView", "type": "component", "shadcn_base": "Calendar", "props": ["events"], "description": "Calendar view"},
                {"name": "CommentThread", "type": "component", "shadcn_base": "Card", "props": ["blockId", "comments"], "description": "Block comments"},
                {"name": "CoverImage", "type": "component", "shadcn_base": "Card", "props": ["imageUrl", "onChange"], "description": "Page cover image"},
                {"name": "EmojiPicker", "type": "component", "shadcn_base": "Popover", "props": ["onSelect"], "description": "Page emoji picker"}
            ],
            "api_endpoints": [
                {"name": "pages.get", "method": "query", "input_schema": "{ pageId: string }", "description": "Get page content", "auth_required": True},
                {"name": "pages.create", "method": "mutation", "input_schema": "{ parentId?: string, title: string }", "description": "Create new page", "auth_required": True},
                {"name": "blocks.update", "method": "mutation", "input_schema": "{ blockId: string, content: any }", "description": "Update block content", "auth_required": True},
                {"name": "blocks.reorder", "method": "mutation", "input_schema": "{ pageId: string, blockIds: string[] }", "description": "Reorder blocks", "auth_required": True},
                {"name": "pages.share", "method": "mutation", "input_schema": "{ pageId: string, email: string, permission: string }", "description": "Share page", "auth_required": True},
                {"name": "comments.add", "method": "mutation", "input_schema": "{ blockId: string, content: string }", "description": "Add comment", "auth_required": True},
                {"name": "search.global", "method": "query", "input_schema": "{ query: string }", "description": "Search all pages", "auth_required": True},
                {"name": "realtime.subscribe", "method": "mutation", "input_schema": "{ pageId: string }", "description": "Subscribe to page updates", "auth_required": True}
            ],
            "database_tables": [
                {"name": "User", "fields": ["id String @id", "email String @unique", "name String", "avatar String?"], "relations": ["pages Page[]", "workspaces WorkspaceMember[]"]},
                {"name": "Workspace", "fields": ["id String @id", "name String", "icon String?"], "relations": ["members WorkspaceMember[]", "pages Page[]"]},
                {"name": "Page", "fields": ["id String @id", "workspaceId String", "parentId String?", "title String", "icon String?", "cover String?", "createdAt DateTime", "updatedAt DateTime"], "relations": ["workspace Workspace", "blocks Block[]"]},
                {"name": "Block", "fields": ["id String @id", "pageId String", "type String", "content Json", "order Int"], "relations": ["page Page"]},
                {"name": "Permission", "fields": ["id String @id", "pageId String", "userId String", "level String"], "relations": ["page Page", "user User"]}
            ],
            "auth_config": {
                "provider": "supabase",
                "strategies": ["email", "google"],
                "protected_routes": ["/*"]
            },
            "deployment_config": {
                "platform": "vercel",
                "env_vars": ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY"],
                "build_command": "npm run build",
                "output_directory": ".next"
            }
        }

    def _job_board_blueprint(self, components: list[str]) -> dict:
        """Job board blueprint"""
        return {
            "ui_components": [
                {"name": "JobCard", "type": "component", "shadcn_base": "Card", "props": ["job", "onApply"], "description": "Job listing card"},
                {"name": "JobList", "type": "page", "shadcn_base": "ScrollArea", "props": ["jobs", "onLoadMore"], "description": "Job listings page"},
                {"name": "ApplicationForm", "type": "feature", "shadcn_base": "Dialog", "props": ["jobId", "onSubmit"], "description": "Job application form"},
                {"name": "ProfileHeader", "type": "component", "shadcn_base": "Card", "props": ["user"], "description": "User profile header"},
                {"name": "ExperienceCard", "type": "component", "shadcn_base": "Card", "props": ["experience"], "description": "Work experience card"},
                {"name": "SkillBadge", "type": "component", "shadcn_base": "Badge", "props": ["skill", "level"], "description": "Skill badge"},
                {"name": "CompanyLogo", "type": "component", "shadcn_base": "Avatar", "props": ["company"], "description": "Company logo display"},
                {"name": "SearchFilters", "type": "component", "shadcn_base": "Accordion", "props": ["filters", "onApply"], "description": "Job search filters"},
                {"name": "SavedJobs", "type": "page", "shadcn_base": "Card", "props": ["jobs"], "description": "Saved jobs list"},
                {"name": "ApplicationStatus", "type": "component", "shadcn_base": "Badge", "props": ["status"], "description": "Application status badge"},
                {"name": "ResumeUploader", "type": "component", "shadcn_base": "Input", "props": ["onUpload"], "description": "Resume file uploader"},
                {"name": "EducationCard", "type": "component", "shadcn_base": "Card", "props": ["education"], "description": "Education history card"}
            ],
            "api_endpoints": [
                {"name": "jobs.list", "method": "query", "input_schema": "{ filters?: object, cursor?: string }", "description": "List jobs", "auth_required": False},
                {"name": "jobs.get", "method": "query", "input_schema": "{ jobId: string }", "description": "Get job details", "auth_required": False},
                {"name": "jobs.apply", "method": "mutation", "input_schema": "{ jobId: string, resumeUrl: string, coverLetter?: string }", "description": "Apply to job", "auth_required": True},
                {"name": "applications.list", "method": "query", "input_schema": "{ cursor?: string }", "description": "List applications", "auth_required": True},
                {"name": "profile.update", "method": "mutation", "input_schema": "{ bio?: string, skills?: string[], experience?: object[] }", "description": "Update profile", "auth_required": True},
                {"name": "jobs.save", "method": "mutation", "input_schema": "{ jobId: string }", "description": "Save job", "auth_required": True},
                {"name": "companies.get", "method": "query", "input_schema": "{ companyId: string }", "description": "Get company details", "auth_required": False},
                {"name": "search.jobs", "method": "query", "input_schema": "{ query: string, location?: string }", "description": "Search jobs", "auth_required": False}
            ],
            "database_tables": [
                {"name": "User", "fields": ["id String @id", "email String @unique", "name String", "headline String?", "bio String?", "resumeUrl String?", "skills String[]"], "relations": ["applications Application[]", "experience Experience[]"]},
                {"name": "Company", "fields": ["id String @id", "name String", "logo String?", "description String", "website String?", "size String?", "industry String?"], "relations": ["jobs Job[]"]},
                {"name": "Job", "fields": ["id String @id", "companyId String", "title String", "description String", "location String", "type String", "salary String?", "skills String[]", "createdAt DateTime"], "relations": ["company Company", "applications Application[]"]},
                {"name": "Application", "fields": ["id String @id", "userId String", "jobId String", "status String", "resumeUrl String", "coverLetter String?", "createdAt DateTime"], "relations": ["user User", "job Job"]},
                {"name": "Experience", "fields": ["id String @id", "userId String", "company String", "title String", "startDate DateTime", "endDate DateTime?", "description String?"], "relations": ["user User"]}
            ],
            "auth_config": {
                "provider": "supabase",
                "strategies": ["email", "google", "linkedin"],
                "protected_routes": ["/profile", "/applications", "/saved"]
            },
            "deployment_config": {
                "platform": "vercel",
                "env_vars": ["DATABASE_URL", "SUPABASE_URL", "SUPABASE_ANON_KEY"],
                "build_command": "npm run build",
                "output_directory": ".next"
            }
        }

    def _social_app_blueprint(self, components: list[str]) -> dict:
        """Generic social app blueprint"""
        return self._twitter_blueprint(components)

    async def synthesize(self, spec: str, swarm_results: list[dict]) -> dict:
        """
        Main synthesis method - turns swarm results into code blueprint.
        Uses Fireworks.ai when available, falls back to templates otherwise.
        """
        try:
            if self.config.api_key:
                prompt = self._build_synthesis_prompt(spec, swarm_results)
                blueprint = await self._call_fireworks_api(prompt)
                print("[OK] Synthesis completed via Fireworks.ai")
            else:
                blueprint = self._generate_fallback_blueprint(spec, swarm_results)
                print("[OK] Synthesis completed via fallback templates")

            return blueprint

        except Exception as e:
            print(f"[WARN] Synthesis API error: {e}, using fallback")
            return self._generate_fallback_blueprint(spec, swarm_results)

        finally:
            await self._close_session()


# Standalone test
if __name__ == "__main__":
    async def test_synthesis():
        engine = CodeSynthesisEngine()
        swarm_results = [
            {"components": ["PostCard", "Timeline"], "patterns": {"auth": "supabase"}, "styles": {"primary": "#1DA1F2"}}
        ]
        blueprint = await engine.synthesize("Twitter clone with Hindi support", swarm_results)
        print(json.dumps(blueprint, indent=2))

    asyncio.run(test_synthesis())
