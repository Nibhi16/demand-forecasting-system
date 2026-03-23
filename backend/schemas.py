from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


AllocationDecision = Literal["Increase riders", "Maintain", "Reduce riders"]


class PredictInput(BaseModel):
    """
    Request schema for a single demand prediction.
    """

    model_config = ConfigDict(extra="forbid")

    week: int = Field(..., ge=0)
    center_id: int
    meal_id: int
    lag_1: float
    lag_2: float


class PredictResponse(BaseModel):
    """
    Response schema for a single prediction + allocation decision.
    """

    predicted_demand: float
    allocation_decision: AllocationDecision

