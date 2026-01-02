from enum import Enum
from typing import List, Literal, Optional
from pydantic import BaseModel, Field

class ExecutionTarget(str, Enum):
    REDDIT_REACTOR = "REDDIT_REACTOR"
    SHOPIFY_SYNC = "SHOPIFY_SYNC"
    TWITTER_SWARM = "TWITTER_SWARM"
    SYSTEM_CORE = "SYSTEM_CORE"

class ActionCommand(BaseModel):
    module: ExecutionTarget
    operation: Literal["START", "STOP", "SCALE", "AUDIT"]
    parameters: dict = Field(default_factory=dict, description="Specific parameters like budget, keywords, target_id")

class NeuralPayload(BaseModel):
    intent_summary: str = Field(..., description="One-sentence summary of commander intent")
    commands: List[ActionCommand]
    risk_level: int = Field(..., ge=0, le=10, description="Risk level (0-10)")
    approval_required: bool = Field(..., description="Whether manual approval is required")
