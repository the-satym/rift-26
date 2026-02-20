import os
import json
import requests

# HuggingFace Inference API - free tier
HF_TOKEN = "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"

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "meta-llama/Llama-3.1-8B-Instruct"

# Phenotype abbreviation map
PHENOTYPE_ABBREV = {
    "Poor Metabolizer": "PM",
    "Intermediate Metabolizer": "IM",
    "Normal Metabolizer": "NM",
    "Ultrarapid Metabolizer": "URM",
    "Rapid Metabolizer": "RM",
    "Normal Function": "NM",
    "Decreased Function": "IM",
    "Poor Function": "PM",
    "Unknown": "Unknown"
}

# Confidence scores based on how complete the data is
CONFIDENCE_MAP = {
    ("known_star", "known_phenotype"): 0.95,
    ("known_star", "Unknown"):         0.50,
    ("unknown_star", "known_phenotype"): 0.60,
    ("unknown_star", "Unknown"):        0.20,
}

def _calculate_confidence(star_allele, phenotype):
    star_key = "unknown_star" if star_allele in (None, "Unknown") else "known_star"
    phenotype_key = "Unknown" if phenotype == "Unknown" else "known_phenotype"
    return CONFIDENCE_MAP.get((star_key, phenotype_key), 0.20)


def generate_llm_explanation(drug, gene, star_allele, phenotype, rsid, risk_label, action):
    """
    Calls HuggingFace Inference API (Mistral-7B) to generate a structured clinical explanation.
    Returns a dict with summary, mechanism, and patient_note.
    """
    prompt = f"""You are a clinical pharmacogenomics assistant. A patient has been analyzed for drug-gene interactions.

Patient Data:
- Drug: {drug}
- Gene: {gene}
- Star Allele (Diplotype): {star_allele}
- Phenotype: {phenotype}
- Detected Variant (rsID): {rsid}
- Risk Assessment: {risk_label}
- Recommended Action: {action}

Generate a clinical explanation in STRICT JSON format with exactly these three fields:
{{
  "summary": "2-3 sentence overview of the drug-gene interaction and what it means for this patient.",
  "mechanism": "1-2 sentences explaining the biological mechanism of how this gene variant affects drug metabolism.",
  "patient_note": "1 sentence in simple non-technical language that a patient could understand."
}}

Return ONLY valid JSON. No markdown, no code blocks, no extra text."""

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 400,
        "temperature": 0.3
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        raw = response.json()["choices"][0]["message"]["content"].strip()

        # Strip markdown code blocks if model wraps in them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()

        parsed = json.loads(raw)

        return {
            "summary": parsed.get("summary", "No summary available."),
            "mechanism": parsed.get("mechanism", "No mechanism data available."),
            "patient_note": parsed.get("patient_note", "Please consult your doctor for details.")
        }

    except json.JSONDecodeError:
        return {
            "summary": "Explanation could not be parsed.",
            "mechanism": "N/A",
            "patient_note": "Please consult your doctor for details."
        }
    except Exception as e:
        return {
            "summary": f"LLM call failed: {str(e)}",
            "mechanism": "N/A",
            "patient_note": "Please consult your doctor for details."
        }


if __name__ == "__main__":
    # Quick test
    result = generate_llm_explanation(
        drug="CLOPIDOGREL",
        gene="CYP2C19",
        star_allele="*2/*4",
        phenotype="Poor Metabolizer",
        rsid="rs4244285",
        risk_label="Toxic/Ineffective",
        action="Avoid. High risk of cardiovascular events."
    )
    print(json.dumps(result, indent=2))