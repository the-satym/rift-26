import pandas as pd


def extract_target_variants(vcf_path):
    target_genes = ['CYP2D6', 'CYP2C19', 'CYP2C9', 'SLCO1B1', 'TPMT', 'DPYD']

    data_lines = []
    header = None

    # 1. Read manually to destroy any space/tab formatting issues
    try:
        with open(vcf_path, 'r') as file:
            for line in file:
                if line.startswith('##'):
                    continue
                if line.startswith('#CHROM'):
                    # .split() automatically handles any mix of spaces and tabs
                    header = line.strip().split()
                    continue
                if header:
                    data_lines.append(line.strip().split())
    except Exception as e:
        raise Exception(f"Failed to read file: {str(e)}")

    if not header:
        raise Exception("Invalid VCF: Missing #CHROM header line.")

    # 2. Build the DataFrame cleanly
    df = pd.DataFrame(data_lines, columns=header)

    if '#CHROM' in df.columns:
        df = df.rename(columns={'#CHROM': 'CHROM'})

    if 'INFO' not in df.columns:
        raise Exception("Invalid VCF format: Missing mandatory 'INFO' column.")

    # 3. Filter for our target genes
    df['INFO'] = df['INFO'].fillna('')
    pattern = '|'.join(target_genes)

    # .copy() prevents memory warnings down the line
    filtered_df = df[df['INFO'].str.contains(pattern, na=False)].copy()

    return filtered_df