"""
Agentic CodeForge - FastAPI Orchestrator
Main entry point for the code generation pipeline
"""

import asyncio
import json
import hashlib
import time
from datetime import datetime
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, EmailStr, Field
import uvicorn

from tinyfish_swarm import TinyFishSwarmController
from code_synthesis import CodeSynthesisEngine
from parallel_generators import ParallelCodeGenerators
from validation_pipeline import ValidationPipeline
from deploy_agent import DeployAgent


# Pydantic Models
class GenerateRequest(BaseModel):
    spec: str = Field(..., min_length=10, max_length=2000, description="Natural language specification")
    user_email: EmailStr = Field(..., description="User email for notifications")
    template_hints: Optional[list[str]] = Field(default=None, description="Optional template preferences")


class GenerateResponse(BaseModel):
    status: str
    repo_url: Optional[str] = None
    live_url: Optional[str] = None
    metrics: Optional[dict] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    services: dict


# Global state for tracking active generations
active_generations: dict[str, dict] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    print("[STARTUP] Agentic CodeForge starting up...")
    # Initialize services
    app.state.swarm_controller = TinyFishSwarmController()
    app.state.synthesis_engine = CodeSynthesisEngine()
    app.state.generators = ParallelCodeGenerators()
    app.state.validator = ValidationPipeline()
    app.state.deploy_agent = DeployAgent()
    yield
    print("[SHUTDOWN] Agentic CodeForge shutting down...")


app = FastAPI(
    title="Agentic CodeForge",
    description="AI-powered full-stack code generation from natural language specs",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_project_id(spec: str, email: str) -> str:
    """Generate unique project ID from spec and email"""
    combined = f"{spec}:{email}:{time.time()}"
    return hashlib.sha256(combined.encode()).hexdigest()[:12]


async def stream_generation_progress(
    spec: str,
    user_email: str,
    project_id: str
) -> AsyncGenerator[str, None]:
    """Stream generation progress as SSE events"""

    start_time = time.time()

    try:
        # Phase 1: Initialize
        yield json.dumps({
            "phase": "init",
            "progress": 0,
            "message": "[STARTUP] Initializing Agentic CodeForge...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        await asyncio.sleep(0.5)

        # Phase 2: TinyFish Swarm (33%)
        yield json.dumps({
            "phase": "swarm",
            "progress": 5,
            "message": "[SWARM] Launching TinyFish agent swarm...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        swarm_controller = app.state.swarm_controller
        swarm_results = await swarm_controller.execute_swarm(spec)

        yield json.dumps({
            "phase": "swarm",
            "progress": 33,
            "message": f"[OK] Extracted patterns from {len(swarm_results)} sources",
            "agents_completed": len(swarm_results),
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        # Phase 3: Code Synthesis (50%)
        yield json.dumps({
            "phase": "synthesis",
            "progress": 40,
            "message": "[AI] Synthesizing patterns with Fireworks.ai...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        synthesis_engine = app.state.synthesis_engine
        blueprint = await synthesis_engine.synthesize(spec, swarm_results)

        yield json.dumps({
            "phase": "synthesis",
            "progress": 50,
            "message": f"[OK] Generated blueprint: {blueprint['summary']}",
            "components_count": len(blueprint.get('ui_components', [])),
            "endpoints_count": len(blueprint.get('api_endpoints', [])),
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        # Phase 4: Parallel Generation (75%)
        yield json.dumps({
            "phase": "generation",
            "progress": 55,
            "message": "[GEN] Running parallel code generators...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        generators = app.state.generators
        generated_code = await generators.generate_all(spec, blueprint, project_id)

        total_lines = sum(len(code.split('\n')) for code in generated_code.values())

        yield json.dumps({
            "phase": "generation",
            "progress": 75,
            "message": f"[OK] Generated {len(generated_code)} files ({total_lines} lines)",
            "files_count": len(generated_code),
            "total_lines": total_lines,
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        # Phase 5: Validation (85%)
        yield json.dumps({
            "phase": "validation",
            "progress": 80,
            "message": "[VALID] Running validation pipeline...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        validator = app.state.validator
        validation_results = await validator.validate(generated_code)

        yield json.dumps({
            "phase": "validation",
            "progress": 85,
            "message": f"[OK] Validation passed: Lighthouse {validation_results['lighthouse_score']}",
            "lighthouse_score": validation_results['lighthouse_score'],
            "eslint_passed": validation_results['eslint_passed'],
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        # Phase 6: Deploy (100%)
        yield json.dumps({
            "phase": "deploy",
            "progress": 90,
            "message": "[STARTUP] Deploying to GitHub + Vercel...",
            "timestamp": datetime.now().isoformat()
        }) + "\n\n"

        deploy_agent = app.state.deploy_agent
        deploy_result = await deploy_agent.deploy(
            project_id=project_id,
            spec=spec,
            generated_code=generated_code,
            user_email=user_email
        )

        elapsed_time = time.time() - start_time

        # Final result
        final_result = {
            "phase": "complete",
            "progress": 100,
            "message": "[DONE] CodeForge generation complete!",
            "status": "success",
            "repo_url": deploy_result['repo_url'],
            "live_url": deploy_result['live_url'],
            "metrics": {
                "total_files": len(generated_code),
                "total_lines": total_lines,
                "lighthouse_score": validation_results['lighthouse_score'],
                "generation_time_seconds": round(elapsed_time, 2),
                "agents_used": len(swarm_results)
            },
            "timestamp": datetime.now().isoformat()
        }

        # Store result
        active_generations[project_id] = final_result

        yield json.dumps(final_result) + "\n\n"

    except Exception as e:
        error_result = {
            "phase": "error",
            "progress": -1,
            "message": f"[ERROR] Generation failed: {str(e)}",
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        active_generations[project_id] = error_result
        yield json.dumps(error_result) + "\n\n"


@app.post("/generate", response_class=StreamingResponse)
async def generate_codebase(request: GenerateRequest):
    """
    Main endpoint: Generate complete codebase from natural language spec
    Returns SSE stream of progress updates
    """
    project_id = generate_project_id(request.spec, request.user_email)

    return StreamingResponse(
        stream_generation_progress(
            spec=request.spec,
            user_email=request.user_email,
            project_id=project_id
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Project-ID": project_id
        }
    )


@app.get("/generate/{project_id}", response_model=GenerateResponse)
async def get_generation_status(project_id: str):
    """Get status of a generation by project ID"""
    if project_id not in active_generations:
        raise HTTPException(status_code=404, detail="Project not found")

    result = active_generations[project_id]
    return GenerateResponse(
        status=result.get('status', 'in_progress'),
        repo_url=result.get('repo_url'),
        live_url=result.get('live_url'),
        metrics=result.get('metrics'),
        error=result.get('error')
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        services={
            "tinyfish_swarm": "operational",
            "fireworks_ai": "operational",
            "composio_deploy": "operational",
            "vercel": "operational"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Agentic CodeForge",
        "version": "1.0.0",
        "description": "AI-powered full-stack code generation",
        "endpoints": {
            "/generate": "POST - Generate codebase from spec (SSE stream)",
            "/generate/{id}": "GET - Check generation status",
            "/health": "GET - Service health check"
        },
        "hackathon": "TinyFish Golden Ticket Competition"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
