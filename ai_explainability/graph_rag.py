import datetime

# Mock localized knowledge graph reflecting actual Indian aviation factors
KNOWLEDGE_GRAPH = {
    "2024-05-13": {
        "event": "ATF (Aviation Turbine Fuel) Tariff Hike",
        "impact": "General 6% price hike passed onto base fares across all routes.",
        "category": "Macroeconomic Costs"
    },
    "holiday_weekend": {
        "start": "2024-05-20",
        "end": "2024-05-25",
        "event": "Buddha Purnima & Domestic Summer Holidays Peak",
        "impact": "Surging holiday travel passenger traffic triggers extreme pricing limits on DEL-BOM & DEL-BLR.",
        "category": "Seasonal Market Demand"
    }
}

def explain_price_movement(date_str: str) -> dict:
    """
    Simulates semantic GraphRAG lookups to explain price variance.
    """
    reasons = []
    categories = []
    
    try:
        t_date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    # Verify macroeconomic fuel issues
    fuel_date = datetime.datetime.strptime("2024-05-13", "%Y-%m-%d").date()
    if t_date >= fuel_date:
        reasons.append(f"Tariff Impact: {KNOWLEDGE_GRAPH['2024-05-13']['event']} - {KNOWLEDGE_GRAPH['2024-05-13']['impact']}")
        categories.append(KNOWLEDGE_GRAPH['2024-05-13']['category'])
        
    # Verify holiday season dates
    hol_start = datetime.datetime.strptime(KNOWLEDGE_GRAPH['holiday_weekend']['start'], "%Y-%m-%d").date()
    hol_end = datetime.datetime.strptime(KNOWLEDGE_GRAPH['holiday_weekend']['end'], "%Y-%m-%d").date()
    if hol_start <= t_date <= hol_end:
        reasons.append(f"Traffic Surge: {KNOWLEDGE_GRAPH['holiday_weekend']['event']} - {KNOWLEDGE_GRAPH['holiday_weekend']['impact']}")
        categories.append(KNOWLEDGE_GRAPH['holiday_weekend']['category'])
        
    if not reasons:
        return {
            "explanation": "Pricing index levels correspond to normal, baseline consumer traffic dynamics.",
            "categories": ["Baseline Dynamics"]
        }
        
    return {
        "explanation": " AND ".join(reasons),
        "categories": list(set(categories))
    }
