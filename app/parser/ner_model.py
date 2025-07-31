# app/parser/ner_model.py

import re

def extract_info(query: str, domain: str = "insurance") -> dict:
    if domain == "insurance":
        # Extract age
        age_match = re.search(r'(\d{2})[- ]?year[- ]?old', query.lower())
        age = int(age_match.group(1)) if age_match else None

        # Extract procedure (very basic for now)
        procedures = ['knee surgery', 'heart surgery', 'hip replacement', 'bypass surgery']
        procedure = next((p for p in procedures if p in query.lower()), 'unknown')

        # Extract location
        locations = ['Pune', 'Delhi', 'Mumbai', 'Bangalore', 'Chennai']
        location = next((loc for loc in locations if loc.lower() in query.lower()), 'unknown')

        # Extract policy duration
        duration_match = re.search(r'(\d+)[ -]?month[- ]?old insurance policy', query.lower())
        policy_duration = int(duration_match.group(1)) if duration_match else None

        return {
            "age": age,
            "procedure": procedure,
            "location": location,
            "policy_duration_months": policy_duration
        }
    elif domain == "legal":
        # Placeholder for legal domain extraction logic
        # Example: extract parties, case type, date, etc.
        # This should be replaced with actual legal NER logic
        return {
            "parties": [],
            "case_type": "unknown",
            "date": None,
            "jurisdiction": "unknown"
        }
    else:
        raise ValueError(f"Unsupported domain: {domain}")
