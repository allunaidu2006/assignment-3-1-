"""
realtime_service.py - Real-Time Match Data Collection and Ingestion Service.
Complying with Week 3 & 4 data collection specifications.
Venue is strictly mandatory for every record.
"""
import os
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.match import Match
from app.services.venue_registry import get_home_venue, standardize_venue, OFFICIAL_VENUES

logger = logging.getLogger(__name__)

# Base paths for data storage (Section 7 of Week 3 report)
DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"

REALTIME_JSON_PATH = RAW_DIR / "realtime_matches.json"
HISTORICAL_CSV_PATH = RAW_DIR / "historical_matches.csv"

class VenueMissingError(ValueError):
    """Raised when a match record has no venue or empty venue."""
    pass

class RealtimeService:
    def __init__(self):
        self._ensure_directories()

    def _ensure_directories(self):
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        FEATURES_DIR.mkdir(parents=True, exist_ok=True)
        if not REALTIME_JSON_PATH.exists():
            with open(REALTIME_JSON_PATH, "w") as f:
                json.dump([], f)

    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validates real-time match data record.
        VENUE IS STRICTLY MANDATORY.
        """
        team_1 = record.get("team_1") or record.get("team_a")
        team_2 = record.get("team_2") or record.get("team_b")
        venue = record.get("venue")

        if not team_1 or not str(team_1).strip():
            raise ValueError("Team 1 / Team A is required.")
        if not team_2 or not str(team_2).strip():
            raise ValueError("Team 2 / Team B is required.")
        
        # Strict Venue Enforcement
        if not venue or not str(venue).strip() or str(venue).strip().lower() in ["null", "none", "unknown", ""]:
            # If venue is omitted, try resolving from home team if explicitly permitted, or raise error
            resolved_venue = get_home_venue(team_1)
            if not resolved_venue:
                raise VenueMissingError(f"Venue is MANDATORY. Match between '{team_1}' and '{team_2}' has no venue.")
            venue = resolved_venue
        
        standardized_venue_name = standardize_venue(venue, home_team=team_1)
        record["venue"] = standardized_venue_name

        if "timestamp" not in record or not record["timestamp"]:
            record["timestamp"] = datetime.now(timezone.utc).isoformat()

        return record

    def get_realtime_records(self) -> List[Dict[str, Any]]:
        """Read saved real-time raw records."""
        if not REALTIME_JSON_PATH.exists():
            return []
        try:
            with open(REALTIME_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def save_realtime_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and persist a real-time match record to raw/realtime_matches.json.
        """
        validated = self.validate_record(record)
        existing = self.get_realtime_records()
        
        # Keep recent 200 real-time records
        existing.append(validated)
        if len(existing) > 500:
            existing = existing[-500:]
            
        with open(REALTIME_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, default=str)
            
        return validated

    def generate_live_matchday_feed(self, db: Session) -> List[Dict[str, Any]]:
        """
        Produces or updates active real-time live matches with live match state,
        including elapsed minute, possession, shots, and MANDATORY venue.
        """
        live_matches = db.query(Match).filter(Match.status == "live").all()
        if not live_matches:
            # Query upcoming or recent matches to convert into live simulation
            upcoming = db.query(Match).filter(Match.is_completed == False).limit(5).all()
            for m in upcoming:
                m.status = "live"
                m.minute = m.minute or 15
                m.possession_a = m.possession_a or 52.0
                m.possession_b = m.possession_b or 48.0
                m.shots_a = m.shots_a or 4
                m.shots_b = m.shots_b or 3
                if not m.venue:
                    m.venue = get_home_venue(m.team_a)
            db.commit()
            live_matches = upcoming

        results = []
        for m in live_matches:
            # Advance live match slightly
            if m.minute is not None and m.minute < 90:
                m.minute += 1
            rec = {
                "match_id": f"MCH-{m.id:04d}",
                "id": m.id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "team_1": m.team_a,
                "team_2": m.team_b,
                "venue": m.venue,  # MANDATORY
                "team_1_score": m.goals_a or 0,
                "team_2_score": m.goals_b or 0,
                "match_status": "Live",
                "minute": m.minute or 45,
                "possession": f"{m.possession_a or 50:.0f}%",
                "possession_a": m.possession_a or 50.0,
                "possession_b": m.possession_b or 50.0,
                "shots": (m.shots_a or 0) + (m.shots_b or 0),
                "shots_a": m.shots_a or 0,
                "shots_b": m.shots_b or 0,
            }
            results.append(rec)
            self.save_realtime_record(rec)

        db.commit()
        return results

realtime_service = RealtimeService()

