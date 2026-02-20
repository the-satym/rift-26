from flask import Flask, flash, Blueprint, redirect, url_for, render_template, session, request, jsonify


from models import Doc,db
from logic.main_pipeline import run_pharmacogenomics_pipeline

doc_bp = Blueprint('doc', __name__, url_prefix='/doc')

import tempfile
import os

@doc_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session.get('user_type') != 'doctor':
        flash('Unauthorized access.', 'error')
        return redirect(url_for('auth.doctor_login'))

    user_id = session.get('user_id')
    doc = Doc.query.filter_by(user_id=user_id).first()

    if request.method == 'POST':
        vcf  = request.files.get('vcf_file')
        drug = request.form.get('drug')

        try:
            # Save FileStorage to a real temp file on disk
            with tempfile.NamedTemporaryFile(delete=False, suffix='.vcf') as tmp:
                vcf.save(tmp.name)
                tmp_path = tmp.name

            output = run_pharmacogenomics_pipeline(tmp_path, drug)
            return jsonify(output)

        except Exception as e:
            print("PIPELINE ERROR:", e)
            return jsonify({"error": str(e)}), 500

        finally:
            # Always clean up the temp file
            if 'tmp_path' in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)

    return render_template('dashboard/doc_dash.html', doc=doc)


