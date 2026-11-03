from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.match import Match
from app.services.analytics_service import (
    get_team_form_chart, get_head_to_head_chart, get_accuracy_over_time,
    get_model_metrics, get_prediction_history, get_team_list
)
from app.services.ml_service import ml_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/team-form/{team_name}")
def team_form(team_name: str, n: int = 10, db: Session = Depends(get_db)):
    return get_team_form_chart(db, team_name, n)

@router.get("/head-to-head")
def head_to_head(team_a: str, team_b: str, db: Session = Depends(get_db)):
    return get_head_to_head_chart(db, team_a, team_b)

@router.get("/accuracy-trend")
def accuracy_trend(db: Session = Depends(get_db)):
    return get_accuracy_over_time(db)

@router.get("/metrics")
def metrics(db: Session = Depends(get_db)):
    return get_model_metrics(db)

@router.get("/teams")
def teams(db: Session = Depends(get_db)):
    return get_team_list(db)

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    metrics_data = get_model_metrics(db)
    recent = get_prediction_history(db, limit=5)
    teams_lst = get_team_list(db)
    active_matches = db.query(Match).filter(Match.is_completed == False).count()
    total_teams = len(teams_lst)
    return {
        "total_predictions": metrics_data["total_predictions"],
        "accuracy": metrics_data["accuracy"],
        "active_matches": active_matches,
        "total_teams": total_teams,
        "model_status": "trained" if ml_service.is_trained() else "not_trained",
        "recent_predictions": recent,
        "top_teams": teams_lst[:5] if len(teams_lst) >= 5 else teams_lst,
    }

