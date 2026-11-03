"""
seed_data.py (Migration wrapper)
Runs the unified real-time dataset pipeline with mandatory venue.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.seed_data import main

if __name__ == "__main__":
    main()
