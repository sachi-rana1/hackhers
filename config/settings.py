import os

# --- System Metadata ---
APP_NAME = "APIx System"
DEBUG = os.getenv("DEBUG", "True") == "True"

# --- Database Credentials ---
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/apix_db")

# --- Flight Corridor Constants & Official DGCA Traffic Weights ---
ROUTE_WEIGHTS = {
    'DEL-BOM': 0.35,  # Delhi - Mumbai (35% weight)
    'DEL-BLR': 0.25,  # Delhi - Bengaluru (25% weight)
    'BOM-BLR': 0.18,  # Mumbai - Bengaluru (18% weight)
    'DEL-CCU': 0.12,  # Delhi - Kolkata (12% weight)
    'BLR-HYD': 0.10   # Bengaluru - Hyderabad (10% weight)
}

AIRLINES = ['IndiGo', 'Air India', 'SpiceJet', 'Akasa Air', 'Air India Express']
SOURCES = ['Direct Airline', 'MakeMyTrip', 'EaseMyTrip', 'Yatra', 'Cleartrip', 'ixigo']
LEAD_TIMES = ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']
