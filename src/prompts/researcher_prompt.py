COMPETITOR_EXTRACT_PROMPT = """
You are a strict data extraction agent. 
Your ONLY job is to extract competitor names from the context and return them as a JSON object with a single key "competitors" mapping to a list of strings.
Do NOT add explanations, do NOT add pricing, do NOT add founders.
Find as many competitors as possible.

Context:
{competitor_data}

Return STRICTLY like this. Example:

Output: "Competitor 1, Competitor 2"

Always extract all the competitors mentioned in the provided context, just for example I have given only 2.
"""