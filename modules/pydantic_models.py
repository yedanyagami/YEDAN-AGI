"""
YEDAN V1300 - PydanticAI Models
Structured output validation for the Tri-Core Neuro-Stack.
"""
from typing import Literal, Optional
from pydantic import BaseModel, Field

class MimicryConfig(BaseModel):
    """Browser-Use human mimicry parameters"""
    mouse_curve: Literal["Bezier", "Linear", "Random"] = "Bezier"
    typing_delay_sec: float = Field(default=0.15, ge=0.05, le=1.0)
    typo_injected: bool = False
    cognitive_delay_sec: float = Field(default=25.0, ge=15.0, le=45.0)

class PricingStrategy(BaseModel):
    """Anxiety-driven dynamic pricing"""
    price: float = Field(..., ge=29.99, le=349.99)
    rationale: str
    compliance_flag: bool = Field(default=False, description="True if compliance/legal risk involved")

class HiveAction(BaseModel):
    """
    Master output schema for YEDAN V1300.
    All reactor outputs MUST conform to this structure.
    """
    tool_used: Literal["Crawl4AI", "Browser-Use", "PydanticAI", "Simulation"]
    target_thread: str
    panic_score: int = Field(..., ge=1, le=10, description="Anxiety index 1-10")
    
    # PydanticAI ensures pricing logic is correct
    pricing_strategy: Optional[PricingStrategy] = None
    
    # Browser-Use execution parameters
    mimicry_config: MimicryConfig = Field(default_factory=MimicryConfig)
    
    # Generated content
    generated_reply: str
    
    # Metadata
    platform: Literal["reddit", "twitter", "shopify"] = "reddit"
    simulation_mode: bool = False

class SensorResult(BaseModel):
    """Output from Crawl4AI sensor"""
    thread_id: str
    title: str
    body_markdown: str
    author: str
    panic_score: int = Field(default=1, ge=1, le=10)
    keywords_matched: list[str] = []
    
class ExecutorResult(BaseModel):
    """Output from Browser-Use executor"""
    success: bool
    action_taken: Literal["reply", "upvote", "skip", "error"]
    screenshot_path: Optional[str] = None
    latency_ms: int = 0
