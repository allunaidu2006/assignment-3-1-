from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from app.models.match import Match
from app.services.venue_registry import get_home_venue, standardize_venue

def get_team_stats(db: Session, team_name: str) -> dict:
    matches = db.query(Match).filter(
        and_(or_(Match.team_a == team_name, Match.team_b == team_name), Match.is_completed == True)
    ).all()
    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0
    
    for m in matches:
        ga = m.goals_a or 0
        gb = m.goals_b or 0
        if m.team_a == team_name:
            goals_scored += ga
            goals_conceded += gb
            if m.outcome == "team_a": wins += 1
            elif m.outcome == "draw": draws += 1
            else: losses += 1
        else:
            goals_scored += gb
            goals_conceded += ga
            if m.outcome == "team_b": wins += 1
            elif m.outcome == "draw": draws += 1
            else: losses += 1
            
    return {
        "wins": wins, "draws": draws, "losses": losses,
        "goals_scored": goals_scored, "goals_conceded": goals_conceded,
        "total_matches": len(matches)
    }

def get_rolling_form(db: Session, team_name: str, n: int = 5) -> dict:
    matches = db.query(Match).filter(
        and_(or_(Match.team_a == team_name, Match.team_b == team_name), Match.is_completed == True)
    ).order_by(Match.match_date.desc()).limit(n).all()
    
    wins = draws = losses = goals_scored = goals_conceded = 0
    for m in matches:
        ga = m.goals_a or 0
        gb = m.goals_b or 0
        if m.team_a == team_name:
            goals_scored += ga
            goals_conceded += gb
            if m.outcome == "team_a": wins += 1
            elif m.outcome == "draw": draws += 1
            else: losses += 1
        else:
            goals_scored += gb
            goals_conceded += ga
            if m.outcome == "team_b": wins += 1
            elif m.outcome == "draw": draws += 1
            else: losses += 1
            
    total = len(matches)
    return {
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "goals_scored_avg": goals_scored / total if total > 0 else 0.0,
        "goals_conceded_avg": goals_conceded / total if total > 0 else 0.0
    }

def get_head_to_head(db: Session, team_a: str, team_b: str) -> dict:
    matches = db.query(Match).filter(
        and_(
            or_(
                and_(Match.team_a == team_a, Match.team_b == team_b),
                and_(Match.team_a == team_b, Match.team_b == team_a)
            ),
            Match.is_completed == True
        )
    ).order_by(Match.match_date.desc()).all()
    
    team_a_wins = team_b_wins = draws = 0
    last_5 = []
    
    for i, m in enumerate(matches):
        res = "draw"
        if m.team_a == team_a and m.outcome == "team_a":
            team_a_wins += 1; res = team_a
        elif m.team_a == team_a and m.outcome == "team_b":
            team_b_wins += 1; res = team_b
        elif m.team_b == team_a and m.outcome == "team_b":
            team_a_wins += 1; res = team_a
        elif m.team_b == team_a and m.outcome == "team_a":
            team_b_wins += 1; res = team_b
        else:
            draws += 1
        if i < 5:
            last_5.append({"date": m.match_date.isoformat() if hasattr(m.match_date, 'isoformat') else str(m.match_date), "result": res})
            
    return {
        "total": len(matches),
        "team_a_wins": team_a_wins,
        "team_b_wins": team_b_wins,
        "draws": draws,
        "last_5": last_5
    }

def get_venue_stats(db: Session, team_name: str, venue: str) -> dict:
    """
    Computes team performance at this specific MANDATORY venue.
    """
    if not venue or not venue.strip():
        raise ValueError("Venue is strictly mandatory for computing venue statistics.")

    matches = db.query(Match).filter(
        and_(Match.venue == venue, or_(Match.team_a == team_name, Match.team_b == team_name), Match.is_completed == True)
    ).all()
    
    wins = 0
    goals_for = 0
    goals_against = 0
    for m in matches:
        ga = m.goals_a or 0
        gb = m.goals_b or 0
        if m.team_a == team_name:
            goals_for += ga
            goals_against += gb
            if m.outcome == "team_a": wins += 1
        elif m.team_b == team_name:
            goals_for += gb
            goals_against += ga
            if m.outcome == "team_b": wins += 1
            
    total = len(matches)
    return {
        "matches_played": total,
        "win_rate": wins / total if total > 0 else 0.0,
        "avg_goals_for": goals_for / total if total > 0 else 0.0,
        "avg_goals_against": goals_against / total if total > 0 else 0.0
    }

def compute_features(db: Session, team_a: str, team_b: str, venue: str) -> Dict[str, Any]:
    """
    Compute full ML feature vector.
    Venue is NOT optional; it is MANDATORY and strictly validated.
    """
    if not venue or not venue.strip():
        raise ValueError("Venue is mandatory and cannot be empty for feature computation.")

    norm_venue = standardize_venue(venue, home_team=team_a)

    a_form = get_rolling_form(db, team_a)
    b_form = get_rolling_form(db, team_b)
    h2h = get_head_to_head(db, team_a, team_b)
    a_venue = get_venue_stats(db, team_a, norm_venue)
    b_venue = get_venue_stats(db, team_b, norm_venue)
    
    h2h_total = h2h["total"]
    
    # Calculate venue home advantage (Week 5: Home advantage feature)
    a_home_venue = get_home_venue(team_a)
    b_home_venue = get_home_venue(team_b)
    is_a_home = 1.0 if norm_venue.lower() == a_home_venue.lower() else 0.0
    is_b_home = 1.0 if norm_venue.lower() == b_home_venue.lower() else 0.0
    venue_home_advantage = is_a_home - is_b_home
    
    features = {
        "team_a_form_wins": a_form["wins"],
        "team_a_form_draws": a_form["draws"],
        "team_a_form_losses": a_form["losses"],
        "team_a_goals_scored_avg": a_form["goals_scored_avg"],
        "team_a_goals_conceded_avg": a_form["goals_conceded_avg"],
        "team_b_form_wins": b_form["wins"],
        "team_b_form_draws": b_form["draws"],
        "team_b_form_losses": b_form["losses"],
        "team_b_goals_scored_avg": b_form["goals_scored_avg"],
        "team_b_goals_conceded_avg": b_form["goals_conceded_avg"],
        "h2h_team_a_wins": h2h["team_a_wins"],
        "h2h_team_b_wins": h2h["team_b_wins"],
        "h2h_draws": h2h["draws"],
        "h2h_total": h2h_total,
        "h2h_team_a_win_ratio": h2h["team_a_wins"] / h2h_total if h2h_total > 0 else 0.0,
        "h2h_team_b_win_ratio": h2h["team_b_wins"] / h2h_total if h2h_total > 0 else 0.0,
        "team_a_venue_win_rate": a_venue["win_rate"],
        "team_b_venue_win_rate": b_venue["win_rate"],
        "venue_home_advantage": venue_home_advantage,
        "form_diff": a_form["wins"] - b_form["wins"],
        "goal_diff_avg": a_form["goals_scored_avg"] - b_form["goals_scored_avg"]
    }
    return features

def get_feature_names() -> List[str]:
    return [
        "team_a_form_wins", "team_a_form_draws", "team_a_form_losses",
        "team_a_goals_scored_avg", "team_a_goals_conceded_avg",
        "team_b_form_wins", "team_b_form_draws", "team_b_form_losses",
        "team_b_goals_scored_avg", "team_b_goals_conceded_avg",
        "h2h_team_a_wins", "h2h_team_b_wins", "h2h_draws", "h2h_total",
        "h2h_team_a_win_ratio", "h2h_team_b_win_ratio",
        "team_a_venue_win_rate", "team_b_venue_win_rate",
        "venue_home_advantage",
        "form_diff", "goal_diff_avg"
    ]
