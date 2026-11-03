"""
venue_registry.py - Master registry for official football venues / stadiums.
Ensures that venue is MANDATORY and verified across historical, real-time,
and prediction workflows.
"""
from typing import Dict, Optional, List

OFFICIAL_VENUES: Dict[str, Dict[str, str | int]] = {
    "Arsenal": {
        "venue": "Emirates Stadium",
        "city": "London",
        "capacity": 60704
    },
    "Aston Villa": {
        "venue": "Villa Park",
        "city": "Birmingham",
        "capacity": 42682
    },
    "Bournemouth": {
        "venue": "Vitality Stadium",
        "city": "Bournemouth",
        "capacity": 11364
    },
    "Brentford": {
        "venue": "Gtech Community Stadium",
        "city": "Brentford",
        "capacity": 17250
    },
    "Brighton": {
        "venue": "Amex Stadium",
        "city": "Brighton",
        "capacity": 31876
    },
    "Burnley": {
        "venue": "Turf Moor",
        "city": "Burnley",
        "capacity": 21944
    },
    "Chelsea": {
        "venue": "Stamford Bridge",
        "city": "London",
        "capacity": 40341
    },
    "Crystal Palace": {
        "venue": "Selhurst Park",
        "city": "London",
        "capacity": 25486
    },
    "Everton": {
        "venue": "Goodison Park",
        "city": "Liverpool",
        "capacity": 39572
    },
    "Fulham": {
        "venue": "Craven Cottage",
        "city": "London",
        "capacity": 25700
    },
    "Ipswich": {
        "venue": "Portman Road",
        "city": "Ipswich",
        "capacity": 30014
    },
    "Leicester": {
        "venue": "King Power Stadium",
        "city": "Leicester",
        "capacity": 32261
    },
    "Liverpool": {
        "venue": "Anfield",
        "city": "Liverpool",
        "capacity": 61276
    },
    "Luton": {
        "venue": "Kenilworth Road",
        "city": "Luton",
        "capacity": 12000
    },
    "Manchester City": {
        "venue": "Etihad Stadium",
        "city": "Manchester",
        "capacity": 53400
    },
    "Manchester United": {
        "venue": "Old Trafford",
        "city": "Manchester",
        "capacity": 74310
    },
    "Newcastle": {
        "venue": "St. James' Park",
        "city": "Newcastle upon Tyne",
        "capacity": 52305
    },
    "Nottm Forest": {
        "venue": "City Ground",
        "city": "Nottingham",
        "capacity": 30445
    },
    "Sheffield Utd": {
        "venue": "Bramall Lane",
        "city": "Sheffield",
        "capacity": 32050
    },
    "Southampton": {
        "venue": "St. Mary's Stadium",
        "city": "Southampton",
        "capacity": 32384
    },
    "Tottenham": {
        "venue": "Tottenham Hotspur Stadium",
        "city": "London",
        "capacity": 62850
    },
    "West Ham": {
        "venue": "London Stadium",
        "city": "London",
        "capacity": 62500
    },
    "Wolves": {
        "venue": "Molineux Stadium",
        "city": "Wolverhampton",
        "capacity": 32050
    }
}

# Aliases for robust name resolution
TEAM_ALIASES: Dict[str, str] = {
    "Man City": "Manchester City",
    "Man Utd": "Manchester United",
    "Man United": "Manchester United",
    "Spurs": "Tottenham",
    "Tottenham Hotspur": "Tottenham",
    "Brighton and Hove Albion": "Brighton",
    "Brighton & Hove Albion": "Brighton",
    "West Ham United": "West Ham",
    "Newcastle United": "Newcastle",
    "Wolverhampton Wanderers": "Wolves",
    "Nottingham Forest": "Nottm Forest",
    "Sheffield United": "Sheffield Utd",
    "AFC Bournemouth": "Bournemouth",
}

VENUE_ALIASES: Dict[str, str] = {
    "Etihad": "Etihad Stadium",
    "Old Trafford": "Old Trafford",
    "Anfield": "Anfield",
    "Emirates": "Emirates Stadium",
    "Stamford Bridge": "Stamford Bridge",
    "Tottenham Stadium": "Tottenham Hotspur Stadium",
    "St James' Park": "St. James' Park",
    "St James Park": "St. James' Park",
    "Villa Park": "Villa Park",
    "Craven Cottage": "Craven Cottage",
    "Goodison Park": "Goodison Park",
    "London Stadium": "London Stadium",
    "Molineux": "Molineux Stadium",
    "Gtech Stadium": "Gtech Community Stadium",
    "Amex": "Amex Stadium",
}

def standardize_team_name(name: str) -> str:
    cleaned = name.strip()
    return TEAM_ALIASES.get(cleaned, cleaned)

def get_home_venue(team_name: str) -> str:
    std_name = standardize_team_name(team_name)
    info = OFFICIAL_VENUES.get(std_name)
    if info:
        return str(info["venue"])
    return f"{team_name} Stadium"

def standardize_venue(venue_name: Optional[str], home_team: Optional[str] = None) -> str:
    """
    Standardize and enforce mandatory venue.
    If venue is missing or empty and home_team is provided, resolve official venue.
    Otherwise raise ValueError.
    """
    if venue_name and venue_name.strip():
        cleaned = venue_name.strip()
        return VENUE_ALIASES.get(cleaned, cleaned)
    
    if home_team and home_team.strip():
        return get_home_venue(home_team)
    
    raise ValueError("Venue is mandatory and cannot be null or empty.")

def get_all_venues_list() -> List[Dict[str, str | int]]:
    result = []
    for team, data in OFFICIAL_VENUES.items():
        result.append({
            "team": team,
            "venue": str(data["venue"]),
            "city": str(data["city"]),
            "capacity": int(data["capacity"])
        })
    return sorted(result, key=lambda x: str(x["venue"]))

