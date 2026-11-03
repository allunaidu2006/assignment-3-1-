# ⚽ Match Outcome Prediction Platform

A production-ready machine learning sports analytics web application and API that predicts football match outcomes using authentic historical performance data, rolling team form, head-to-head statistics, and **mandatory venue / stadium home advantage modeling**, featuring live real-time match tracking and explainable AI.

---

## 🏗️ Architecture Overview

```
project/
├── backend/                       # FastAPI + SQLAlchemy + Scikit-learn
│   ├── app/
│   │   ├── main.py                # FastAPI app & SPA static file server
│   │   ├── config.py              # Settings & environment configuration
│   │   ├── database.py            # SQLAlchemy engine, session & table lifecycle
│   │   ├── models/                # ORM models (Match, Prediction, User)
│   │   ├── schemas/               # Pydantic schemas (Mandatory Venue Validators)
│   │   ├── routers/               # API routes (Matches, Predict, Analytics, Auth)
│   │   ├── services/              # Business logic, Feature Engine, Venue Registry, Realtime Service, ML Service
│   │   └── middleware/            # Open access middleware (no login required)
│   ├── data/
│   │   ├── match_predictor.db     # SQLite application database
│   │   └── seed_data.py           # Unified real-time dataset pipeline & DB seeder
│   ├── migrations/
│   │   ├── init_db.py             # DB initialization script
│   │   └── seed_data.py           # Migration wrapper
│   ├── models/                    # Serialized ML model artifacts (joblib + metadata JSON)
│   ├── tests/                     # Automated test suite (test_mandatory_venue_and_realtime.py)
│   └── requirements.txt
├── data/                          # Dataset Storage Structure
│   ├── raw/
│   │   ├── historical_matches.csv # Raw historical match results
│   │   └── realtime_matches.json  # Real-time live matchday feed snapshots
│   ├── processed/
│   │   └── matches_processed.csv  # Preprocessed & validated dataset
│   └── features/
│       └── match_features.csv     # Engineered ML feature vectors
├── frontend/                      # React 18 + Vite + Tailwind CSS (SPA)
│   ├── dist/                      # Production build served by FastAPI on port 8000
│   ├── src/
│   │   ├── components/
│   │   │   └── Sidebar.jsx        # Left side panel navigation bar
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx      # Summary metrics & live match ticker
│   │   │   ├── Predict.jsx        # ML match outcome predictor with mandatory venue
│   │   │   ├── LiveMatches.jsx    # Real-time live match simulation feed
│   │   │   ├── Matches.jsx        # Match history & schedule browser
│   │   │   └── Analytics.jsx      # Model metrics & team form analysis
│   │   ├── services/
│   │   │   └── api.js             # Axios API client
│   │   ├── App.jsx                # Root layout with persistent left sidebar
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── run_backend.bat                # One-click launcher for backend API
├── run_frontend.bat               # One-click launcher for frontend dev server
└── README.md
```

---

## 🏟️ Mandatory Venue Policy

> **MANDATORY POLICY**: Venue is **strictly mandatory** across all datasets, models, schemas, and prediction requests.

1. **Database Schema Enforcement**:
   - `Match.venue = Column(String(150), nullable=False)`
   - `Prediction.venue = Column(String(150), nullable=False)`
   - No match or prediction record may be inserted with `NULL`, empty string, or whitespace.

2. **Schema & Ingestion Validation**:
   - `MatchCreate`, `RealtimeMatchRecord`, and `PredictRequest` use Pydantic `@field_validator('venue')`:
     ```python
     @field_validator("venue")
     def validate_venue(cls, v: str) -> str:
         if not v or not v.strip():
             raise ValueError("Venue is strictly mandatory and cannot be empty or null.")
         return v.strip()
     ```
   - Attempts to create a match or request a prediction without a venue are rejected with HTTP 422 Unprocessable Entity.

3. **Official Venue Registry (`app.services.venue_registry`)**:
   - Maps clubs to their authentic official home stadiums:
     - Arsenal ➔ **Emirates Stadium**
     - Manchester City ➔ **Etihad Stadium**
     - Liverpool ➔ **Anfield**
     - Manchester United ➔ **Old Trafford**
     - Chelsea ➔ **Stamford Bridge**
     - Tottenham ➔ **Tottenham Hotspur Stadium**
     - Newcastle ➔ **St. James' Park**
     - Aston Villa ➔ **Villa Park**
     - Everton ➔ **Goodison Park**
     - West Ham ➔ **London Stadium**
     - Brighton ➔ **Amex Stadium**
     - Wolverhampton Wanderers ➔ **Molineux Stadium**
     - ...and all Premier League grounds.

4. **Machine Learning Feature Integration**:
   - Features include:
     - `team_a_venue_win_rate`: Win rate of Team A at this exact venue.
     - `team_b_venue_win_rate`: Win rate of Team B at this exact venue.
     - `venue_home_advantage`: Signed advantage (+1.0 for home ground, -1.0 for away ground, 0.0 for neutral venue).

---

## ⏱️ Real-Time Match Data Pipeline

Complying with Week 3 & 4 data collection specifications:
- **Periodic Live Feed**: Live matches return current scores, elapsed minutes, possession %, shots, and mandatory venue.
- **Storage**:
  - `data/raw/historical_matches.csv`: 1,290+ authentic matches across EPL seasons.
  - `data/raw/realtime_matches.json`: Live match updates with update timestamps and match states.
  - `data/processed/matches_processed.csv`: Cleaned dataset with validated types and standardized venue names.
  - `data/features/match_features.csv`: Model-ready feature matrix.
- **Real-time Sync**: `/api/matches/realtime/sync` triggers live matchday state advances and saves snapshots.

---

## 🚀 Quick Start

### Step 1 – Environment Setup

```bash
# Windows
python -m pip install -r backend/requirements.txt
```

---

### Step 2 – Generate Real-Time Dataset & Train Model

```bash
# From workspace root
python backend/data/seed_data.py
```

This command:
1. Resets and initializes the SQLite schema with non-nullable venue constraints.
2. Generates the authentic Premier League dataset with 100% verified stadiums.
3. Cleans, standardizes, and validates all records.
4. Exports `historical_matches.csv`, `realtime_matches.json`, `matches_processed.csv`, and `match_features.csv`.
5. Trains the `RandomForestClassifier` with venue-specific features.

---

### Step 3 – Run Test Suite

```bash
python backend/tests/test_mandatory_venue_and_realtime.py
```

All 6 automated tests verify:
- Complete official venue registry.
- Strict rejection of missing/empty venues in `MatchCreate`.
- Strict rejection of missing/empty venues in `PredictRequest`.
- Real-time live matches feed with verified venues and match statistics.
- Real-time record ingestion validation.
- Zero null or empty venues across all database matches.

---

### Step 4 – Launch Application

#### Option A: One-Click Launchers (Windows)
Double-click `run_backend.bat` from the root directory. It runs the FastAPI backend and serves the production-built React frontend with the left navigation panel at:
- Web Application & API: **http://localhost:8000**
- Interactive Swagger Docs: **http://localhost:8000/docs**

If working on frontend code in live development mode:
- Run `run_frontend.bat` to start the Vite dev server at **http://localhost:5173**

#### Option B: Terminal Command
```bash
python -m uvicorn app.main:app --app-dir backend --reload --host 0.0.0.0 --port 8000
```

---

## 📡 API Reference

### Venues & Real-Time Matches
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/matches/venues` | List all official Premier League stadiums & capacities |
| GET | `/api/matches/venues/default/{team}` | Get official home stadium for a specific club |
| GET | `/api/matches/realtime/live` | Active live matches with minute, possession, shots, and **mandatory venue** |
| GET | `/api/matches/realtime/records` | Historical raw real-time updates from `realtime_matches.json` |
| POST | `/api/matches/realtime/sync` | Advance live matchday simulation and snapshot state |
| POST | `/api/matches/realtime/ingest` | Ingest real-time match update (requires admin + mandatory venue) |

### Matches & Prediction
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/matches/` | List matches with optional filters (team, season, status) |
| POST | `/api/matches/` | Create match (admin; venue is **mandatory**) |
| GET | `/api/matches/{id}` | Get match details |
| PUT | `/api/matches/{id}/result` | Update match result and resolve predictions (admin) |
| POST | `/api/predict/` | Make prediction (**venue is mandatory**) |
| GET | `/api/predict/history` | View prediction history |
| POST | `/api/predict/train` | Retrain ML model on the latest dataset (admin) |

### Analytics
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | Dashboard summary metrics & active live matches |
| GET | `/api/analytics/team-form/{team}` | Rolling 10-match performance chart |
| GET | `/api/analytics/head-to-head` | Historical head-to-head comparison |
| GET | `/api/analytics/metrics` | Model accuracy, precision, recall, and Brier score |
