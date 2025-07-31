# app/reasoner/output_generator.py

def format_output(evaluation, structured_query):
    output = {
        "input": structured_query,
        "decision": evaluation["decision"],
        "amount": evaluation["amount"],
        "justification": "Decision based on the following clause(s):",
        "clauses": evaluation["clauses"]
    }
    # Add legal-specific fields if present
    if "parties" in evaluation:
        output["parties"] = evaluation["parties"]
    if "organizations" in evaluation:
        output["organizations"] = evaluation["organizations"]
    if "jurisdiction" in evaluation:
        output["jurisdiction"] = evaluation["jurisdiction"]
    if "dates" in evaluation:
        output["dates"] = evaluation["dates"]
    return output
