# app/reasoner/evaluator.py
import re
import spacy
nlp = spacy.load("en_core_web_sm")

def evaluate(structured_query, clauses, domain="insurance"):
    if domain == "insurance":
        age = structured_query.get("age")
        procedure = structured_query.get("procedure")
        duration = structured_query.get("policy_duration_months")

        decision = "rejected"
        amount = 0
        matching_clauses = []

        for clause in clauses:
            clause_text = clause.lower()

            if "knee surgery" in clause_text and "6 months" in clause_text:
                if duration and duration >= 6:
                    decision = "approved"
                    amount = 15000
                    matching_clauses.append(clause)
                else:
                    matching_clauses.append(clause)

            elif "emergency" in clause_text and "from day 1" in clause_text:
                if "emergency" in procedure.lower():
                    decision = "approved"
                    amount = 10000
                    matching_clauses.append(clause)

        return {
            "decision": decision,
            "amount": amount,
            "clauses": matching_clauses
        }
    elif domain == "legal":
        parties = set()
        organizations = set()
        dates = set()
        jurisdiction = None
        for clause in clauses:
            # Use spaCy to extract person names, organizations, dates, and GPEs
            doc = nlp(clause)
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    parties.add(ent.text)
                if ent.label_ == "ORG":
                    organizations.add(ent.text)
                if ent.label_ == "DATE":
                    dates.add(ent.text)
                if ent.label_ == "GPE" and not jurisdiction:
                    jurisdiction = ent.text
            # Fallback: keyword matching for jurisdiction
            if not jurisdiction and "jurisdiction" in clause.lower():
                # Try to extract the location after 'jurisdiction of'
                import re
                match = re.search(r'jurisdiction of ([A-Za-z\s]+)', clause, re.IGNORECASE)
                if match:
                    jurisdiction = match.group(1).strip()
                else:
                    jurisdiction = clause
        return {
            "decision": "info_extracted",
            "amount": None,
            "clauses": clauses,
            "parties": list(parties),
            "organizations": list(organizations),
            "dates": list(dates),
            "jurisdiction": jurisdiction
        }
    else:
        raise ValueError(f"Unsupported domain: {domain}")
