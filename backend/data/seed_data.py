"""
seed_data.py - Real-Time Dataset Generator and DB Seeder.
Mandatory Venue Enforcement across all matches and predictions.
Generates:
- data/raw/historical_matches.csv
- data/raw/realtime_matches.json
- data/processed/matches_processed.csv
- data/features/match_features.csv
- Populates SQLite database with real Premier League clubs and verified stadiums.
"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, reset_tables
from app.services.data_pipeline import (
    generate_premier_league_dataset,
    clean_and_validate_dataset,
    export_datasets,
    sync_to_database,
    compute_and_export_features
)
from app.services.ml_service import ml_service

def main():
    print("=" * 60)
    print("Resetting and Initializing Database & Tables (Enforcing Mandatory Venue)...")
    reset_tables()
    
    print("Generating Authentic Premier League Dataset (Venue is Mandatory)...")
    raw_matches = generate_premier_league_dataset()
    print(f"Generated {len(raw_matches)} raw match records.")
    
    print("Cleaning and Validating Dataset (Verifying Mandatory Venues)...")
    cleaned_matches = clean_and_validate_dataset(raw_matches)
    print(f"Cleaned and verified {len(cleaned_matches)} match records.")
    
    print("Exporting Datasets to CSV & JSON (data/raw, data/processed)...")
    export_datasets(cleaned_matches)
    
    print("Synchronizing with Database...")
    db = SessionLocal()
    try:
        sync_to_database(db, cleaned_matches)
        
        print("Computing and Exporting Features (data/features)...")
        compute_and_export_features(db)
        
        print("Training Machine Learning Model with Mandatory Venue Features...")
        train_res = ml_service.train(db)
        print(f"Model Training Results: {train_res}")
        
    finally:
        db.close()

    print("=" * 60)
    print("Real-time dataset pipeline completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
