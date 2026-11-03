"""
test_mandatory_venue_and_realtime.py
Direct verification script without testclient transport delays.
"""
import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal
from app.models.match import Match
from app.models.prediction import Prediction
from app.schemas.match import MatchCreate, RealtimeMatchRecord
from app.schemas.prediction import PredictRequest
from app.services.venue_registry import get_all_venues_list, get_home_venue, standardize_venue
from app.services.feature_engine import compute_features
from app.services.ml_service import ml_service
from app.services.realtime_service import realtime_service, VenueMissingError
from pydantic import ValidationError

class TestMandatoryVenueAndRealtime(unittest.TestCase):
    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_01_venue_registry_completeness(self):
        """Verify official stadiums registry contains verified venues for all EPL clubs."""
        venues = get_all_venues_list()
        self.assertGreaterEqual(len(venues), 20)
        stadium_names = [v["venue"] for v in venues]
        self.assertIn("Emirates Stadium", stadium_names)
        self.assertIn("Etihad Stadium", stadium_names)
        self.assertIn("Anfield", stadium_names)
        self.assertIn("Old Trafford", stadium_names)
        self.assertIn("Stamford Bridge", stadium_names)
        print("✓ PASS: Official venue registry lists all verified Premier League stadiums.")

    def test_02_mandatory_venue_enforced_in_schemas(self):
        """Verify that MatchCreate strictly rejects missing, empty, or whitespace venues."""
        # 1. Missing venue
        with self.assertRaises(ValidationError):
            MatchCreate(
                team_a="Arsenal",
                team_b="Chelsea",
                match_date=datetime.now()
            )

        # 2. Empty string venue
        with self.assertRaises(ValidationError):
            MatchCreate(
                team_a="Arsenal",
                team_b="Chelsea",
                venue="",
                match_date=datetime.now()
            )

        # 3. Whitespace string venue
        with self.assertRaises(ValidationError):
            MatchCreate(
                team_a="Arsenal",
                team_b="Chelsea",
                venue="   ",
                match_date=datetime.now()
            )

        # 4. Valid venue
        m = MatchCreate(
            team_a="Arsenal",
            team_b="Chelsea",
            venue="Emirates Stadium",
            match_date=datetime.now()
        )
        self.assertEqual(m.venue, "Emirates Stadium")
        print("✓ PASS: MatchCreate schema strictly mandates venue and rejects empty/whitespace values.")

    def test_03_mandatory_venue_enforced_in_prediction(self):
        """Verify that PredictRequest strictly rejects missing, empty, or whitespace venues."""
        # Missing venue
        with self.assertRaises(ValidationError):
            PredictRequest(team_a="Liverpool", team_b="Manchester City")

        # Empty venue
        with self.assertRaises(ValidationError):
            PredictRequest(team_a="Liverpool", team_b="Manchester City", venue="")

        # Whitespace venue
        with self.assertRaises(ValidationError):
            PredictRequest(team_a="Liverpool", team_b="Manchester City", venue="   ")

        # Valid venue
        req = PredictRequest(team_a="Liverpool", team_b="Manchester City", venue="Anfield")
        self.assertEqual(req.venue, "Anfield")

        # Test prediction computation with mandatory venue
        feats = compute_features(self.db, req.team_a, req.team_b, req.venue)
        self.assertIn("team_a_venue_win_rate", feats)
        self.assertIn("venue_home_advantage", feats)
        self.assertEqual(feats["venue_home_advantage"], 1.0)  # Anfield is Liverpool's home!

        pred_res = ml_service.predict(feats)
        self.assertIn("predicted_outcome", pred_res)
        self.assertIn("confidence", pred_res)
        self.assertIn("top_features", pred_res)
        print(f"✓ PASS: Prediction succeeded with mandatory venue 'Anfield' -> Outcome: {pred_res['predicted_outcome']} (Confidence: {pred_res['confidence']:.2f}).")

    def test_04_realtime_matches_feed(self):
        """Verify real-time live feed produces live records with mandatory venue."""
        live_matches = realtime_service.generate_live_matchday_feed(self.db)
        self.assertGreater(len(live_matches), 0)
        for m in live_matches:
            self.assertTrue(bool(m.get("venue")), "Venue must be present in live match record")
            self.assertNotEqual(m["venue"].strip(), "")
            self.assertEqual(m["match_status"], "Live")
            self.assertIsNotNone(m["minute"])
            self.assertIsNotNone(m["possession"])
        print(f"✓ PASS: Real-time feed active with {len(live_matches)} matches, all with mandatory venues.")

    def test_05_realtime_ingest_venue_validation(self):
        """Verify real-time ingest rejects missing venue."""
        invalid_rec = {
            "match_id": "MCH-TEST-1",
            "timestamp": datetime.now().isoformat(),
            "team_1": "Arsenal",
            "team_2": "Chelsea",
            "venue": "",  # Empty
            "team_1_score": 1,
            "team_2_score": 0,
            "match_status": "Live"
        }
        with self.assertRaises(ValidationError):
            RealtimeMatchRecord(**invalid_rec)

        valid_rec = {
            "match_id": "MCH-TEST-2",
            "timestamp": datetime.now().isoformat(),
            "team_1": "Arsenal",
            "team_2": "Chelsea",
            "venue": "Emirates Stadium",
            "team_1_score": 1,
            "team_2_score": 0,
            "match_status": "Live"
        }
        rec_obj = RealtimeMatchRecord(**valid_rec)
        saved = realtime_service.save_realtime_record(rec_obj.model_dump())
        self.assertEqual(saved["venue"], "Emirates Stadium")
        print("✓ PASS: Real-time match record strictly enforces mandatory venue.")

    def test_06_database_contains_no_null_venues(self):
        """Verify all matches in the SQLite database have non-null, non-empty venues."""
        null_count = self.db.query(Match).filter((Match.venue == None) | (Match.venue == "")).count()
        self.assertEqual(null_count, 0)
        total = self.db.query(Match).count()
        self.assertGreaterEqual(total, 1000)
        print(f"✓ PASS: Database verified: 0 null/empty venues across {total} matches.")

if __name__ == "__main__":
    unittest.main()
