"""
Test Suite for Agentic CodeForge
Tests for all core modules
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock

# Import modules to test
import sys
sys.path.insert(0, '../backend')

from tinyfish_swarm import TinyFishSwarmController, SwarmConfig
from code_synthesis import CodeSynthesisEngine
from parallel_generators import ParallelCodeGenerators
from validation_pipeline import ValidationPipeline
from deploy_agent import DeployAgent


class TestTinyFishSwarm:
    """Tests for TinyFish Swarm Controller"""

    @pytest.fixture
    def swarm_controller(self):
        config = SwarmConfig(api_key="test-key")
        return TinyFishSwarmController(config)

    def test_select_targets_twitter(self, swarm_controller):
        """Test target selection for Twitter clone spec"""
        targets = swarm_controller._select_targets_for_spec("Twitter clone with real-time posts")
        assert len(targets) > 0
        target_ids = [t["id"] for t in targets]
        assert "github_nextjs" in target_ids or "supabase_docs" in target_ids

    def test_select_targets_ecommerce(self, swarm_controller):
        """Test target selection for ecommerce spec"""
        targets = swarm_controller._select_targets_for_spec("Meesho-style ecommerce with UPI")
        target_ids = [t["id"] for t in targets]
        assert "razorpay_docs" in target_ids

    def test_fallback_components(self, swarm_controller):
        """Test fallback component generation"""
        components = swarm_controller._get_fallback_components("github_nextjs", "Twitter clone")
        assert "PostCard" in components
        assert "Timeline" in components

    def test_fallback_patterns(self, swarm_controller):
        """Test fallback pattern generation"""
        patterns = swarm_controller._get_fallback_patterns("supabase_docs", "Twitter clone")
        assert "auth" in patterns
        assert "supabase" in patterns.get("auth", "")

    @pytest.mark.asyncio
    async def test_execute_swarm(self, swarm_controller):
        """Test swarm execution returns results"""
        results = await swarm_controller.execute_swarm("Simple test app")
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert "source" in result
            assert "components" in result


class TestCodeSynthesis:
    """Tests for Code Synthesis Engine"""

    @pytest.fixture
    def synthesis_engine(self):
        return CodeSynthesisEngine()

    def test_twitter_blueprint(self, synthesis_engine):
        """Test Twitter blueprint generation"""
        blueprint = synthesis_engine._twitter_blueprint([])
        assert "ui_components" in blueprint
        assert "api_endpoints" in blueprint
        assert "database_tables" in blueprint
        assert len(blueprint["ui_components"]) > 5

    def test_ecommerce_blueprint(self, synthesis_engine):
        """Test ecommerce blueprint generation"""
        blueprint = synthesis_engine._ecommerce_blueprint([])
        assert "ui_components" in blueprint
        # Check for payment-related components
        component_names = [c["name"] for c in blueprint["ui_components"]]
        assert "ProductCard" in component_names or "CartDrawer" in component_names

    @pytest.mark.asyncio
    async def test_synthesize_fallback(self, synthesis_engine):
        """Test synthesis with fallback (no API key)"""
        swarm_results = [
            {"components": ["TestComponent"], "patterns": {"auth": "test"}, "styles": {}}
        ]
        blueprint = await synthesis_engine.synthesize("Twitter clone", swarm_results)
        assert "ui_components" in blueprint
        assert "summary" in blueprint


class TestParallelGenerators:
    """Tests for Parallel Code Generators"""

    @pytest.fixture
    def generators(self):
        return ParallelCodeGenerators()

    def test_props_interface_generation(self, generators):
        """Test TypeScript props interface generation"""
        interface = generators._build_props_interface("TestComponent", ["posts", "onLike"])
        assert "interface TestComponentProps" in interface
        assert "posts" in interface
        assert "onLike" in interface

    def test_shadcn_imports(self, generators):
        """Test shadcn import generation"""
        imports = generators._get_shadcn_imports("Card")
        assert "Card" in imports
        assert "@/components/ui/card" in imports

    def test_trpc_router_generation(self, generators):
        """Test tRPC router generation"""
        endpoints = [
            {"name": "posts.list", "method": "query", "input_schema": "{}", "description": "List posts", "auth_required": False}
        ]
        router_code = generators._generate_trpc_router("posts", endpoints)
        assert "postsRouter" in router_code
        assert "list:" in router_code

    @pytest.mark.asyncio
    async def test_generate_all(self, generators):
        """Test full code generation"""
        blueprint = {
            "ui_components": [
                {"name": "TestCard", "type": "component", "shadcn_base": "Card", "props": ["data"], "description": "Test"}
            ],
            "api_endpoints": [],
            "database_tables": [],
            "deployment_config": {"env_vars": ["TEST_VAR"]}
        }
        files = await generators.generate_all("Test app", blueprint, "test123")
        assert len(files) > 0
        assert any("TestCard" in path for path in files.keys())


class TestValidationPipeline:
    """Tests for Validation Pipeline"""

    @pytest.fixture
    def validator(self):
        return ValidationPipeline()

    @pytest.mark.asyncio
    async def test_eslint_validation(self, validator):
        """Test ESLint-like validation"""
        code_files = {
            "test.tsx": 'const x = 1; console.log("test");'
        }
        result = await validator._validate_eslint(code_files)
        assert "passed" in result
        assert "warnings" in result

    @pytest.mark.asyncio
    async def test_lighthouse_score(self, validator):
        """Test Lighthouse score calculation"""
        code_files = {
            "test.tsx": '''
import Image from "next/image";
export const metadata = { title: "Test" };
export default function Page() {
  return <main><Image src="/test.png" alt="Test" loading="lazy" /></main>;
}
'''
        }
        score = await validator._calculate_lighthouse_score(code_files)
        assert isinstance(score, int)
        assert 70 <= score <= 100

    @pytest.mark.asyncio
    async def test_full_validation(self, validator):
        """Test full validation pipeline"""
        code_files = {
            "app/page.tsx": '"use client"; export default function Page() { return <div>Test</div>; }'
        }
        result = await validator.validate(code_files)
        assert "eslint_passed" in result
        assert "lighthouse_score" in result


class TestDeployAgent:
    """Tests for Deploy Agent"""

    @pytest.fixture
    def deploy_agent(self):
        return DeployAgent()

    def test_readme_generation(self, deploy_agent):
        """Test README generation"""
        readme = deploy_agent.generate_readme(
            spec="Test app spec",
            project_id="test123",
            live_url="https://test.vercel.app"
        )
        assert "Test app spec" in readme
        assert "test123" in readme
        assert "https://test.vercel.app" in readme

    @pytest.mark.asyncio
    async def test_deploy_simulation(self, deploy_agent):
        """Test deployment with simulated results (no API keys)"""
        result = await deploy_agent.deploy(
            project_id="test123",
            spec="Test app",
            generated_code={"README.md": "# Test"},
            user_email="test@example.com"
        )
        assert "repo_url" in result
        assert "live_url" in result
        assert "success" in result


class TestIntegration:
    """Integration tests for the full pipeline"""

    @pytest.mark.asyncio
    async def test_full_pipeline_twitter_clone(self):
        """Test full pipeline with Twitter clone spec"""
        spec = "Twitter clone with real-time posts"

        # 1. Swarm extraction
        swarm = TinyFishSwarmController()
        swarm_results = await swarm.execute_swarm(spec)
        assert len(swarm_results) > 0

        # 2. Synthesis
        synthesis = CodeSynthesisEngine()
        blueprint = await synthesis.synthesize(spec, swarm_results)
        assert "ui_components" in blueprint

        # 3. Code generation
        generators = ParallelCodeGenerators()
        files = await generators.generate_all(spec, blueprint, "test123")
        assert len(files) > 10

        # 4. Validation
        validator = ValidationPipeline()
        validation_result = await validator.validate(files)
        assert validation_result["lighthouse_score"] >= 70

    @pytest.mark.asyncio
    async def test_full_pipeline_ecommerce(self):
        """Test full pipeline with ecommerce spec"""
        spec = "Meesho-style ecommerce with UPI payments"

        swarm = TinyFishSwarmController()
        swarm_results = await swarm.execute_swarm(spec)

        synthesis = CodeSynthesisEngine()
        blueprint = await synthesis.synthesize(spec, swarm_results)

        # Check for payment-related patterns
        assert "payments" in str(blueprint).lower() or "razorpay" in str(blueprint).lower()


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--asyncio-mode=auto"])
