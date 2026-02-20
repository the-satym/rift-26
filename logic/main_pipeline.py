from datetime import datetime

from logic.validation import validate_vcf_file
from logic.extractor import extract_target_variants
from logic.phenotype_matching import map_phenotypes
from logic.bridge import pipeline_bridge
from models import Analysis
def generate_patient_id():
    last_patient = Analysis.query.order_by(Analysis.pat_id.desc()).first()
    if not last_patient:
        return "patient_001"

    last_num = int(last_patient.id.split("_")[1])
    new_num = last_num + 1

    # Automatically increase digit length as needed
    digits = max(3, len(str(new_num)))
    return f"patient_{new_num:0{digits}d}"


def run_pharmacogenomics_pipeline(vcf_file_path, requested_drugs_string):
    """
    The Master API Function.
    Coordinates the entire flow from raw VCF file to final clinical JSON output.
    """
    print(f"--- Starting Analysis for Drugs: {requested_drugs_string} ---")

    # STEP 0: Validate the file before anything else
    is_valid, validation_msg = validate_vcf_file(vcf_file_path)
    if not is_valid:
        return {"status": "error", "message": validation_msg}

    try:
        # STEP 1: Extract relevant variants from the VCF
        extracted_df = extract_target_variants(vcf_file_path)

        if extracted_df.empty:
            return {"status": "error", "message": "No relevant CPIC genes found in this VCF file."}

        # STEP 2: Map star alleles to phenotypes
        mapped_df = map_phenotypes(extracted_df)

        # STEP 3: Bridge to clinical rules + LLM explanation
        # Returns a LIST — one complete result object per drug
        results = pipeline_bridge(mapped_df, requested_drugs_string, patient_id=generate_patient_id())

        return results  # List of per-drug JSON objects


    except Exception as e:
        return {"status": "error", "message": f"Pipeline execution failed: {str(e)}"}


# ==========================================
# TEST THE MASTER PIPELINE
# ==========================================
if __name__ == "__main__":
    import json
    start = datetime.now()
    final_output = run_pharmacogenomics_pipeline("test_patient.vcf", "CLOPIDOGREL, CODEINE")
    print(json.dumps(final_output, indent=2))
    end = datetime.now()
    print(f"\nExecution time: {end - start}")