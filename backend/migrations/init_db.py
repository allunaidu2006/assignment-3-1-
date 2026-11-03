import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import create_tables, reset_tables
from app.models import User, Match, Prediction

if __name__ == "__main__":
    create_tables()
    print("Database tables initialized successfully with mandatory venue.")
