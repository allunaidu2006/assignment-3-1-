from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.database import get_db
from app.models.match import Match
from app.models.prediction import Prediction
from app.schemas.match import MatchCreate, MatchUpdate, MatchOut, MatchResultInput, RealtimeMatchRecord, VenueInfo
from app.middleware.auth_middleware import require_admin, require_user
from app.services.analytics_service import get_team_list
from app.services.venue_registry import get_all_venues_list, get_home_venue, standardize_venue
from app.services.realtime_service import realtime_service, VenueMissingError

router = APIRouter(prefix="/api/matches", tags=["matches"])

@router.get("/teams/list", response_model=List[str])
def list_teams(db: Session = Depends(get_db)):
    return get_team_list(db)

@router.get("/venues", response_model=List[VenueInfo])
def list_venues():
    """
    Returns official football venues / stadiums.
    Venue is mandatory for all match predictions and fixtures.
    """
    return get_all_venues_list()

@router.get("/venues/default/{team_name}")
def get_default_venue(team_name: str):
    """
    Returns official default venue for a given football club.
    """
    venue = get_home_venue(team_name)
    return {"team": team_name, "venue": venue, "is_mandatory": True}

@router.get("/realtime/live", response_model=List[Dict[str, Any]])
def get_realtime_live_matches(db: Session = Depends(get_db)):
    """
    Fetch active real-time match records with live possession, shots,
    elapsed minute, and MANDATORY venue.
    """
    return realtime_service.generate_live_matchday_feed(db)

@router.get("/realtime/records", response_model=List[Dict[str, Any]])
def get_realtime_records():
    """
    Returns historical raw real-time update snapshots from data/raw/realtime_matches.json.
    """
    return realtime_service.get_realtime_records()

@router.post("/realtime/sync")
def sync_realtime_matches(db: Session = Depends(get_db), current_user = Depends(require_user)):
    """
    Triggers periodic real-time match data synchronization and state updates.
    """
    updates = realtime_service.generate_live_matchday_feed(db)
    return {
        "status": "success",
        "synced_count": len(updates),
        "venue_verified": True,
        "matches": updates
    }

@router.post("/realtime/ingest", response_model=Dict[str, Any])
def ingest_realtime_match(record: RealtimeMatchRecord, current_user = Depends(require_admin)):
    """
    Ingest a real-time match record into the raw storage.
    VENUE IS STRICTLY MANDATORY.
    """
    try:
        saved = realtime_service.save_realtime_record(record.model_dump())
        return {"status": "ingested", "record": saved}
    except VenueMissingError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[MatchOut])
def list_matches(
    skip: int = 0,
    limit: int = 100,
    team: Optional[str] = None,
    season: Optional[str] = None,
    match_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Match)
    if team:
        query = query.filter((Match.team_a == team) | (Match.team_b == team))
    if season:
        query = query.filter(Match.season == season)
    if match_status:
        query = query.filter(Match.status == match_status)
    return query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()

@router.post("/", response_model=MatchOut)
def create_match(match_in: MatchCreate, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    """
    Create a new match.
    VENUE IS MANDATORY.
    """
    if not match_in.venue or not match_in.venue.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Venue is mandatory and cannot be empty or null."
        )
        
    std_venue = standardize_venue(match_in.venue, home_team=match_in.team_a)
    match_data = match_in.model_dump()
    match_data["venue"] = std_venue
    
    match = Match(**match_data)
    db.add(match)
    db.commit()
    db.refresh(match)
    return match

@router.get("/{match_id}", response_model=MatchOut)
def get_match(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match

@router.put("/{match_id}/result", response_model=MatchOut)
def update_match_result(match_id: int, result_in: MatchResultInput, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    
    match.goals_a = result_in.goals_a
    match.goals_b = result_in.goals_b
    if result_in.goals_a > result_in.goals_b:
        match.outcome = "team_a"
    elif result_in.goals_b > result_in.goals_a:
        match.outcome = "team_b"
    else:
        match.outcome = "draw"
    
    match.is_completed = True
    match.status = "completed"
    match.minute = 90
    db.commit()
    
    # Resolve linked predictions
    preds = db.query(Prediction).filter(Prediction.match_id == match_id, Prediction.actual_outcome == None).all()
    for p in preds:
        p.actual_outcome = match.outcome
        p.is_correct = (p.predicted_outcome == p.actual_outcome)
    db.commit()
    db.refresh(match)
    return match

@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    db.delete(match)
    db.commit()
    return {"ok": True}
