from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator

class MatchCreate(BaseModel):
    team_a: str = Field(..., min_length=2, description="Home team name")
    team_b: str = Field(..., min_length=2, description="Away team name")
    venue: str = Field(..., min_length=2, description="Official match venue / stadium (MANDATORY)")
    match_date: datetime
    season: Optional[str] = None
    status: Optional[str] = "upcoming"
    minute: Optional[int] = None
    possession_a: Optional[float] = None
    possession_b: Optional[float] = None
    shots_a: Optional[int] = None
    shots_b: Optional[int] = None

    @field_validator("venue")
    def validate_venue_mandatory(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Venue is strictly mandatory and cannot be empty or null.")
        return v.strip()

    @field_validator("team_a", "team_b")
    def validate_teams(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Team name cannot be empty.")
        return v.strip()

class MatchUpdate(BaseModel):
    goals_a: Optional[int] = None
    goals_b: Optional[int] = None
    outcome: Optional[str] = None
    is_completed: Optional[bool] = None
    status: Optional[str] = None
    minute: Optional[int] = None
    possession_a: Optional[float] = None
    possession_b: Optional[float] = None
    shots_a: Optional[int] = None
    shots_b: Optional[int] = None

class MatchOut(BaseModel):
    id: int
    team_a: str
    team_b: str
    venue: str  # MANDATORY in response
    match_date: datetime
    season: Optional[str] = None
    goals_a: Optional[int] = None
    goals_b: Optional[int] = None
    outcome: Optional[str] = None
    is_completed: bool
    status: Optional[str] = "completed"
    minute: Optional[int] = None
    possession_a: Optional[float] = None
    possession_b: Optional[float] = None
    shots_a: Optional[int] = None
    shots_b: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MatchResultInput(BaseModel):
    goals_a: int
    goals_b: int

class RealtimeMatchRecord(BaseModel):
    match_id: str
    timestamp: str
    team_1: str
    team_2: str
    venue: str = Field(..., min_length=2, description="Stadium / venue is MANDATORY")
    team_1_score: int
    team_2_score: int
    match_status: str  # 'Live', 'Completed', 'Upcoming'
    minute: Optional[int] = None
    possession: Optional[str] = None
    shots: Optional[int] = None
    recent_form: Optional[str] = None
    head_to_head: Optional[str] = None
    match_result: Optional[str] = None

    @field_validator("venue")
    def validate_realtime_venue(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Venue is strictly mandatory for real-time match records.")
        return v.strip()

class VenueInfo(BaseModel):
    team: str
    venue: str
    city: str
    capacity: Optional[int] = None
