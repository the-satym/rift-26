import pandas as pd


def map_phenotypes(filtered_df):
    # 1. expand=False prevents DataFrame/Series ambiguity
    filtered_df['Star_Allele'] = filtered_df['INFO'].str.extract(r'STAR=(\*[a-zA-Z0-9]+)', expand=False)

    def determine_phenotype(row):
        info_str = str(row['INFO']).upper()
        star = row['Star_Allele']

        # Safe check for missing values
        if pd.isna(star) or not star:
            return "Unknown"

        if "CYP2C19" in info_str:
            mapping = {"*1": "Normal Metabolizer", "*2": "Poor Metabolizer", "*3": "Poor Metabolizer",
                       "*17": "Ultrarapid Metabolizer"}
            return mapping.get(star, "Unknown")

        elif "CYP2D6" in info_str:
            mapping = {"*1": "Normal Metabolizer", "*4": "Poor Metabolizer", "*5": "Poor Metabolizer",
                       "*2xN": "Ultrarapid Metabolizer"}
            return mapping.get(star, "Unknown")

        elif "CYP2C9" in info_str:
            mapping = {"*1": "Normal Metabolizer", "*2": "Intermediate Metabolizer", "*3": "Poor Metabolizer"}
            return mapping.get(star, "Unknown")

        elif "SLCO1B1" in info_str:
            mapping = {"*1": "Normal Function", "*5": "Decreased Function", "*15": "Poor Function"}
            return mapping.get(star, "Unknown")

        elif "TPMT" in info_str:
            mapping = {"*1": "Normal Metabolizer", "*2": "Poor Metabolizer", "*3A": "Poor Metabolizer"}
            return mapping.get(star, "Unknown")

        elif "DPYD" in info_str:
            mapping = {"*1": "Normal Metabolizer", "*2A": "Poor Metabolizer"}
            return mapping.get(star, "Unknown")

        return "Unknown"

    filtered_df['Phenotype'] = filtered_df.apply(determine_phenotype, axis=1)

    return filtered_df