import pandas as pd
from datetime import datetime, timezone
from logic.clinical_recommendation import get_clinical_recommendation
from logic.llm_explainer import generate_llm_explanation, PHENOTYPE_ABBREV, _calculate_confidence

def pipeline_bridge(mapped_df, drug_names_str, patient_id="PATIENT_001"):
    """
    Connects the mapped genetic data to the clinical rule engine and LLM explainer.
    Returns a list of per-drug result objects matching the required JSON schema.
    """
    # 1. Clean up the requested drugs
    drugs_list = [drug.strip().upper() for drug in drug_names_str.split(',')]

    # 2. Map drugs to their target genes
    drug_to_gene_map = {
        "CLOPIDOGREL": "CYP2C19",
        "CODEINE": "CYP2D6",
        "WARFARIN": "CYP2C9",
        "SIMVASTATIN": "SLCO1B1",
        "AZATHIOPRINE": "TPMT",
        "FLUOROURACIL": "DPYD"
    }

    final_results = []

    # 3. Iterate through the requested drugs
    for drug in drugs_list:
        if not drug:
            continue

        timestamp = datetime.now(timezone.utc).isoformat()
        target_gene = drug_to_gene_map.get(drug)

        if not target_gene:
            final_results.append({
                "patient_id": patient_id,
                "drug": drug,
                "timestamp": timestamp,
                "error": "Drug not supported by current CPIC guidelines.",
                "quality_metrics": {"vcf_parsing_success": False}
            })
            continue

        # 4. Find the rows for this gene
        gene_rows = mapped_df[mapped_df['INFO'].str.contains(target_gene, na=False)]

        if gene_rows.empty:
            final_results.append({
                "patient_id": patient_id,
                "drug": drug,
                "timestamp": timestamp,
                "error": f"No genetic data found for {target_gene}.",
                "quality_metrics": {"vcf_parsing_success": True, "variants_detected": 0}
            })
            continue

        # 5. Extract alleles — grab up to 2 rows to build a diplotype
        alleles = []
        rsids = []

        for _, row in gene_rows.iterrows():
            star = row['Star_Allele'] if 'Star_Allele' in row.index else None
            if star and not pd.isna(star):
                alleles.append(star)
            rsid_val = row['ID'] if 'ID' in row.index else 'Unknown'
            rsids.append({"rsid": rsid_val if rsid_val else 'Unknown'})

        # Build diplotype: if 2 alleles found use both, if 1 assume *1 on other chromosome
        if len(alleles) >= 2:
            diplotype = f"{alleles[0]}/{alleles[1]}"
        elif len(alleles) == 1:
            diplotype = f"*1/{alleles[0]}"
        else:
            diplotype = "Unknown"

        # 6. Get phenotype from first match
        first_match = gene_rows.iloc[0]
        patient_phenotype = first_match['Phenotype']
        phenotype_abbrev = PHENOTYPE_ABBREV.get(patient_phenotype, "Unknown")

        # 7. Get clinical recommendation
        clinical_rec = get_clinical_recommendation(drug, patient_phenotype)
        risk_label = clinical_rec.get("risk", "Unknown")
        severity = clinical_rec.get("severity", "low")
        action = clinical_rec.get("action", "Consult standard clinical guidelines.")

        # 8. Calculate confidence score
        primary_star = alleles[0] if alleles else None
        confidence = _calculate_confidence(primary_star, patient_phenotype)

        # 9. Call Gemini LLM for explanation
        primary_rsid = rsids[0]["rsid"] if rsids else "Unknown"
        llm_explanation = generate_llm_explanation(
            drug=drug,
            gene=target_gene,
            star_allele=diplotype,
            phenotype=patient_phenotype,
            rsid=primary_rsid,
            risk_label=risk_label,
            action=action
        )

        # 10. Package into the exact required JSON schema
        final_results.append({
            "patient_id": patient_id,
            "drug": drug,
            "timestamp": timestamp,
            "risk_assessment": {
                "risk_label": risk_label,
                "confidence_score": confidence,
                "severity": severity
            },
            "pharmacogenomic_profile": {
                "primary_gene": target_gene,
                "diplotype": diplotype,
                "phenotype": phenotype_abbrev,
                "detected_variants": rsids
            },
            "clinical_recommendation": {
                "action": action,
                "guideline": "CPIC"
            },
            "llm_generated_explanation": llm_explanation,
            "quality_metrics": {
                "vcf_parsing_success": True,
                "variants_detected": len(rsids),
                "genes_covered": [target_gene],
                "diplotype_resolved": diplotype != "Unknown"
            }
        })

    return final_results