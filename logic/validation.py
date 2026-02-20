import os
def validate_vcf_file(file_path):
    """
    Validates a user-uploaded VCF file before any Pandas processing begins.
    Returns: (is_valid: bool, error_message: str)
    """
    # 1. Check if the file actually exists
    if not os.path.exists(file_path):
        return False, "Error: File does not exist on the server."

    # 2. Check the file extension
    if not file_path.lower().endswith('.vcf'):
        return False, "Error: Invalid file type. Must be a .vcf file."
    # 3. Check the file size (Max 5MB)
    # 5 Megabytes = 5 * 1024 * 1024 Bytes
    max_size_bytes = 5 * 1024 * 1024
    file_size = os.path.getsize(file_path)

    if file_size > max_size_bytes:
        # Calculate actual size for a helpful error message
        actual_mb = file_size / (1024 * 1024)
        return False, f"Error: File size ({actual_mb:.2f} MB) exceeds the 5MB limit."

    # 4. The Nerd Check: Verify the actual VCF header
    # Anyone can rename a .txt file to .vcf. This actually opens the file
    # and reads JUST the first line to ensure it's authentic genomic data.
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline()
            if not first_line.startswith('##fileformat=VCF'):
                return False, "Error: Corrupted or invalid VCF file. Missing standard VCF header."
    except Exception as e:
        return False, f"Error reading file: {str(e)}"

    # If it passes all 4 checks, it's golden.
    return True, "Success: Valid VCF file."

# ==========================================
# HOW TO USE THIS IN YOUR FLASK ROUTE:
# ==========================================
# file_path = "uploads/patient_data.vcf"
# is_valid, msg = validate_vcf_file(file_path)
#
# if not is_valid:
#     print(msg) # Or return this as a JSON error to the frontend
#     # STOP PROCESSING HERE
# else:
#     print("File is safe. Proceeding to Pandas extraction...")
#     # my_variants = extract_target_variants(file_path)