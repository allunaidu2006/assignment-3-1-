from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.prediction import Prediction
from app.models.match import Match
from app.services.feature_engine import get_head_to_head

def get_model_metrics(db: Session) -> Dict[str, Any]:
    preds = db.query(Prediction).filter(Prediction.actual_outcome != None).all()
    if not preds:
        return {
            "accuracy": 0.0, "precision": 0.0, "recall": 0.0,
            "brier_score": 0.0, "total_predictions": 0, "correct_predictions": 0
        }

    correct = sum(1 for p in preds if p.is_correct)
    total = len(preds)

    # Compute weighted precision and recall using sklearn
    try:
        from sklearn.metrics import precision_score, recall_score
        y_true = [p.actual_outcome for p in preds]
        y_pred = [p.predicted_outcome for p in preds]
        precision = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
        recall = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    except Exception:
        precision = correct / total
        recall = correct / total

    # Brier score: mean squared error of probability for the actual class
    brier_sum = 0.0
    for p in preds:
        if p.actual_outcome == "team_a":
            prob = p.prob_team_a
        elif p.actual_outcome == "team_b":
            prob = p.prob_team_b
        else:
            prob = p.prob_draw
        brier_sum += (1.0 - prob) ** 2

    return {
        "accuracy": correct / total,
        "precision": precision,
        "recall": recall,
        "brier_score": brier_sum / total,
        "total_predictions": total,
        "correct_predictions": correct,
    }

def get_prediction_history(db: Session, limit: int = 50) -> List[Dict[str, Any]]:
    preds = db.query(Prediction).order_by(Prediction.created_at.desc()).limit(limit).all()
    return [{"id": p.id, "team_a": p.team_a, "team_b": p.team_b, "predicted": p.predicted_outcome, "actual": p.actual_outcome, "correct": p.is_correct} for p in preds]

def get_team_form_chart(db: Session, team_name: str, n: int = 10) -> Dict[str, Any]:
    matches = db.query(Match).filter(
        ((Match.team_a == team_name) | (Match.team_b == team_name)) & (Match.is_completed == True)
    ).order_by(Match.match_date.desc()).limit(n).all()
    
    wins, draws, losses = 0, 0, 0
    recent_matches = []
    for m in reversed(matches):
        if (m.team_a == team_name and m.outcome == "team_a") or (m.team_b == team_name and m.outcome == "team_b"):
            result = "win"
            wins += 1
        elif m.outcome == "draw":
            result = "draw"
            draws += 1
        else:
            result = "loss"
            losses += 1
        recent_matches.append({
            "date": m.match_date.strftime("%Y-%m-%d") if m.match_date else None,
            "result": result,
            "goals_scored": m.goals_a if m.team_a == team_name else m.goals_b,
            "goals_conceded": m.goals_b if m.team_a == team_name else m.goals_a,
        })
    return {
        "recent_matches": recent_matches,
        "stats": {"wins": wins, "draws": draws, "losses": losses},
    }

def get_head_to_head_chart(db: Session, team_a: str, team_b: str) -> Dict[str, Any]:
    return get_head_to_head(db, team_a, team_b)

def get_accuracy_over_time(db: Session) -> List[Dict[str, Any]]:
    preds = db.query(Prediction).filter(Prediction.actual_outcome != None).order_by(Prediction.created_at.asc()).all()
    res = []
    correct_so_far = 0
    for i, p in enumerate(preds):
        if p.is_correct:
            correct_so_far += 1
        res.append({
            "date": p.created_at.isoformat(),
            "cumulative_accuracy": correct_so_far / (i + 1)
        })
    return res

def get_team_list(db: Session) -> List[str]:
    teams_a = [r[0] for r in db.query(Match.team_a).distinct().all()]
    teams_b = [r[0] for r in db.query(Match.team_b).distinct().all()]
    return sorted(list(set(teams_a + teams_b)))
