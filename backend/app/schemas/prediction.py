from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class PredictRequest(BaseModel):
    team_a: str = Field(..., min_length=2, description="Home team name")
    team_b: str = Field(..., min_length=2, description="Away team name")
    venue: str = Field(..., min_length=2, description="Official match venue / stadium (MANDATORY)")
    match_id: Optional[int] = None

    @field_validator("venue")
    def validate_venue(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Venue is strictly mandatory and cannot be empty or null.")
        return v.strip()

    @field_validator("team_a", "team_b")
    def validate_teams(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Team name cannot be empty.")
        return v.strip()

class FeatureImportance(BaseModel):
    feature_name: str
    importance: float

class PredictResponse(BaseModel):
    predicted_outcome: str
    prob_team_a: float
    prob_team_b: float
    prob_draw: float
    confidence: float
    top_features: List[FeatureImportance]
    prediction_id: int

class PredictionOut(BaseModel):
    id: int
    match_id: Optional[int] = None
    team_a: str
    team_b: str
    venue: str  # MANDATORY
    predicted_outcome: str
    prob_team_a: float
    prob_team_b: float
    prob_draw: float
    confidence: float
    actual_outcome: Optional[str] = None
    is_correct: Optional[bool] = None
    feature_importances: Optional[str] = None
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class PredictionResolve(BaseModel):
    prediction_id: int
    actual_outcome: str

class ModelMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    brier_score: float
    total_predictions: int
    correct_predictions: int
