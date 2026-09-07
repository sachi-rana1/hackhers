import random
from scraping_engine.base_scraper import BaseScraper

class IndigoScraper(BaseScraper):
    def scrape_route(self, route: str, flight_date: str) -> list:
        """
        Simulates parsing direct HTML/API requests from Indigo.
        """
        headers = self.get_headers()
        prices = []
        for lead_time in ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']:
            base_fare = random.uniform(3000, 11000)
            prices.append({
                "flight_date": flight_date,
                "route": route,
                "airline": "IndiGo",
                "source": "Direct Airline",
                "lead_time": lead_time,
                "base_fare": round(base_fare, 2),
                "taxes": round(base_fare * 0.12, 2),
                "udf": 500 if 'DEL' in route else 350,
                "conv_fee": 0.00,
                "total_fare": round(base_fare * 1.12 + (500 if 'DEL' in route else 350), 2)
            })
        return prices
