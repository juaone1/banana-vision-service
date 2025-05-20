from pydantic import BaseModel
from typing import Any, Optional
from uuid import UUID
from datetime import datetime

class InferenceResultOut(BaseModel):
    id: UUID
    created_at: datetime
    regular_result: Optional[Any]
    thermal_result: Optional[Any]
    fused_confidence: Optional[float]
    fusion_decision: Optional[str]
    regular_output_url: Optional[str]
    thermal_output_url: Optional[str]

    class Config:
        orm_mode = True
