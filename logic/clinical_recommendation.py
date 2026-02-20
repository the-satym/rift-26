def get_clinical_recommendation(drug_name, phenotype):
    """
    Takes a SINGLE drug name and a SINGLE phenotype,
    and returns the clinical risk data based on CPIC guidelines.
    """
    # 1. Clean the input (handles weird capitalization or accidental spaces from the bridge)
    drug = str(drug_name).strip().upper()

    # 2. The Master CPIC Dictionary
    cpic_knowledge_base = {
        "CLOPIDOGREL": {
            "Normal Metabolizer": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Poor Metabolizer": {"risk": "Toxic/Ineffective", "severity": "high", "action": "Avoid. High risk of cardiovascular events."},
            "Intermediate Metabolizer": {"risk": "Adjust Dosage", "severity": "moderate", "action": "Consider alternative therapy like prasugrel."}
        },
        "CODEINE": {
            "Normal Metabolizer": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Ultrarapid Metabolizer": {"risk": "Toxic", "severity": "critical", "action": "Avoid. High risk of life-threatening respiratory depression."},
            "Poor Metabolizer": {"risk": "Ineffective", "severity": "moderate", "action": "Avoid. Lack of efficacy."}
        },
        "WARFARIN": {
            "Normal Metabolizer": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Intermediate Metabolizer": {"risk": "Adjust Dosage", "severity": "moderate", "action": "Reduce starting dose by 15-30%."},
            "Poor Metabolizer": {"risk": "Toxic", "severity": "high", "action": "Reduce starting dose by 50-70%. High bleeding risk."}
        },
        "SIMVASTATIN": {
            "Normal Function": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Decreased Function": {"risk": "Adjust Dosage", "severity": "moderate", "action": "Limit dose to 20mg/day. Monitor for muscle toxicity."},
            "Poor Function": {"risk": "Toxic", "severity": "high", "action": "Avoid 80mg dose. High risk of myopathy/rhabdomyolysis."}
        },
        "AZATHIOPRINE": {
            "Normal Metabolizer": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Intermediate Metabolizer": {"risk": "Adjust Dosage", "severity": "moderate", "action": "Start at 30-80% of normal dose."},
            "Poor Metabolizer": {"risk": "Toxic", "severity": "critical", "action": "Start at 10% of normal dose or avoid. High risk of fatal myelosuppression."}
        },
        "FLUOROURACIL": {
            "Normal Metabolizer": {"risk": "Safe", "severity": "none", "action": "Standard dosing."},
            "Intermediate Metabolizer": {"risk": "Adjust Dosage", "severity": "high", "action": "Reduce starting dose by 50%."},
            "Poor Metabolizer": {"risk": "Toxic", "severity": "critical", "action": "Avoid completely. Risk of fatal drug toxicity."}
        }
    }

    # 3. Default fallback if the genetic data is weird or missing
    default_response = {"risk": "Unknown", "severity": "low", "action": "Consult standard clinical guidelines."}

    # 4. Perform the exact lookup and return a single dictionary
    return cpic_knowledge_base.get(drug, {}).get(phenotype, default_response)