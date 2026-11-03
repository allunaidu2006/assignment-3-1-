import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    team_a = Column(String(100), nullable=False)
    team_b = Column(String(100), nullable=False)
    venue = Column(String(150), nullable=False)  # MANDATORY: Official stadium / venue
    predicted_outcome = Column(String(10), nullable=False)
    prob_team_a = Column(Float, nullable=False)
    prob_team_b = Column(Float, nullable=False)
    prob_draw = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    actual_outcome = Column(String(10), nullable=True)
    is_correct = Column(Boolean, nullable=True)
    feature_importances = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    created_by = Column(Integer, ForeignKey("users.id"))

    @property
    def feature_importances_dict(self):
        if self.feature_importances:
            return json.loads(self.feature_importances)
        return []

    @feature_importances_dict.setter
    def feature_importances_dict(self, value):
        self.feature_importances = json.dumps(value)
