from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.prediction import PredictRequest, PredictResponse, PredictionOut, PredictionResolve, ModelMetrics
from app.services.ml_service import ml_service
from app.services.feature_engine import compute_features
from app.services.venue_registry import standardize_venue
from app.services.analytics_service import get_model_metrics
from app.middleware.auth_middleware import require_user, require_admin
from app.models.prediction import Prediction

router = APIRouter(prefix="/api/predict", tags=["predict"])

@router.post("/", response_model=PredictResponse)
def predict_outcome(req: PredictRequest, db: Session = Depends(get_db), current_user = Depends(require_user)):
    if not ml_service.is_trained():
        raise HTTPException(status_code=503, detail="Model is not trained yet. Admin must train the model first.")
    
    # Strict Venue Validation: Venue is mandatory!
    if not req.venue or not req.venue.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Venue is mandatory and cannot be empty or null."
        )

    norm_venue = standardize_venue(req.venue, home_team=req.team_a)
    
    try:
        features = compute_features(db, req.team_a, req.team_b, norm_venue)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    res = ml_service.predict(features)
    
    pred = Prediction(
        match_id=req.match_id,
        team_a=req.team_a,
        team_b=req.team_b,
        venue=norm_venue,
        predicted_outcome=res["predicted_outcome"],
        prob_team_a=res["prob_team_a"],
        prob_team_b=res["prob_team_b"],
        prob_draw=res["prob_draw"],
        confidence=res["confidence"],
        feature_importances_dict=res["top_features"],
        created_by=current_user.id if current_user else 1
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    
    return PredictResponse(
        predicted_outcome=res["predicted_outcome"],
        prob_team_a=res["prob_team_a"],
        prob_team_b=res["prob_team_b"],
        prob_draw=res["prob_draw"],
        confidence=res["confidence"],
        top_features=res["top_features"],
        prediction_id=pred.id
    )

@router.get("/history", response_model=List[PredictionOut])
def prediction_history(db: Session = Depends(get_db)):
    return db.query(Prediction).order_by(Prediction.created_at.desc()).all()

@router.post("/resolve", response_model=PredictionOut)
def resolve_prediction(req: PredictionResolve, db: Session = Depends(get_db), current_user = Depends(require_admin)):
    pred = db.query(Prediction).filter(Prediction.id == req.prediction_id).first()
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")
    pred.actual_outcome = req.actual_outcome
    pred.is_correct = (pred.predicted_outcome == req.actual_outcome)
    db.commit()
    db.refresh(pred)
    return pred

@router.get("/metrics", response_model=ModelMetrics)
def get_metrics(db: Session = Depends(get_db)):
    return get_model_metrics(db)

@router.post("/train")
def train_model(db: Session = Depends(get_db), current_user = Depends(require_admin)):
    result = ml_service.train(db)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
