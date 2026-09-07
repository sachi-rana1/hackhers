import os

APP_NAME = "APIx System"
DEBUG = True

# Database URL (Defaults to local SQLite so it works out-of-the-box!)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./apix_local.db")

# Official DGCA Passenger Traffic Distribution Weights (Sum = 1.0)
ROUTE_WEIGHTS = {
    'DEL-BOM': 0.35,  # Delhi - Mumbai
    'DEL-BLR': 0.25,  # Delhi - Bengaluru
    'BOM-BLR': 0.18,  # Mumbai - Bengaluru
    'DEL-CCU': 0.12,  # Delhi - Kolkata
    'BLR-HYD': 0.10   # Bengaluru - Hyderabad
}

AIRLINES = ['IndiGo', 'Air India', 'SpiceJet', 'Akasa Air', 'Air India Express']
SOURCES = ['Direct Airline', 'MakeMyTrip', 'EaseMyTrip', 'Yatra', 'Cleartrip', 'ixigo']
LEAD_TIMES = ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']
