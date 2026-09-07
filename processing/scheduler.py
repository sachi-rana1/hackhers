import time
import threading
from scraping_engine.airlines.indigo import IndigoScraper
from scraping_engine.otas.makemytrip import MakeMyTripScraper

def run_daily_scraping_job():
    """
    Aggregates data from active scrapers across core routes.
    """
    print("[SCHEDULER] Daily flight fare ingestion triggered...")
    indigo = IndigoScraper()
    mmt = MakeMyTripScraper()
    
    for route in ['DEL-BOM', 'DEL-BLR']:
        data_indigo = indigo.scrape_route(route, "2026-09-07")
        data_mmt = mmt.scrape_route(route, "2026-09-07")
        print(f"[SCHEDULER] Ingested {len(data_indigo) + len(data_mmt)} prices for corridor {route}.")

def start_cron_scheduler():
    """
    Launches a low-overhead background daemon thread to run our scraper loop.
    """
    def loop():
        while True:
            run_daily_scraping_job()
            # Wait 24 hours (86400 seconds) before repeating
            time.sleep(86400)
            
    thread = threading.Thread(target=loop, daemon=True)
    thread.start()
    print("[SCHEDULER] Background service started successfully.")
