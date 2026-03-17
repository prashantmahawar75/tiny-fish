"""
Agentic CodeForge Backend
AI-powered full-stack code generation from natural language specs
"""

__version__ = "1.0.0"
__author__ = "CodeForge Team"

from .main import app
from .tinyfish_swarm import TinyFishSwarmController
from .code_synthesis import CodeSynthesisEngine
from .parallel_generators import ParallelCodeGenerators
from .validation_pipeline import ValidationPipeline
from .deploy_agent import DeployAgent

__all__ = [
    "app",
    "TinyFishSwarmController",
    "CodeSynthesisEngine",
    "ParallelCodeGenerators",
    "ValidationPipeline",
    "DeployAgent",
]
