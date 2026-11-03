from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from app.database import Base

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    team_a = Column(String(100), nullable=False)
    team_b = Column(String(100), nullable=False)
    venue = Column(String(150), nullable=False)  # MANDATORY: Official stadium / venue
    match_date = Column(DateTime, nullable=False)
    season = Column(String(20), nullable=True)
    goals_a = Column(Integer, nullable=True)
    goals_b = Column(Integer, nullable=True)
    outcome = Column(String(10), nullable=True)  # team_a, draw, team_b
    is_completed = Column(Boolean, default=False)
    
    # Real-time match data fields (Week 3/4 Data Specs)
    status = Column(String(20), default="completed")  # 'completed', 'live', 'upcoming'
    minute = Column(Integer, nullable=True)           # Elapsed match minute if live
    possession_a = Column(Float, nullable=True)       # Team A possession %
    possession_b = Column(Float, nullable=True)       # Team B possession %
    shots_a = Column(Integer, nullable=True)          # Team A shots
    shots_b = Column(Integer, nullable=True)          # Team B shots
    
    created_at = Column(DateTime, default=func.now())
