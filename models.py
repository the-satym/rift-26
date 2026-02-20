from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, UTC

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_type = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)
    profile_pic = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

class Doc(db.Model):
    __tablename__ = 'doctors'
    doc_id = db.Column(db.Integer, primary_key = True,autoincrement= True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    name = db.Column(db.String(150))
    gender = db.Column(db.String(150))
    designation = db.Column(db.String(150))
    age = db.Column(db.Integer())
    experience = db.Column(db.Integer())

class Analysis(db.Model):
    __tablename__ = 'analysis'
    analysis_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    pat_id = db.Column(db.String(100))
    doc_id = db.Column(db.Integer, db.ForeignKey("doctors.doc_id"), nullable=False)  # removed unique=True
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    vcf_filename = db.Column(db.String(255), nullable=True)
    vcf_file_path = db.Column(db.String(500), nullable=True)

    drug = db.Column(db.Text(), nullable=False)  # comma-separated
    risk_label = db.Column(db.String(50), nullable=True)  # Safe | Adjust Dosage | Toxic | etc.
    confidence_score = db.Column(db.Float, nullable=True)
    severity = db.Column(db.String(20), nullable=True)  # none|low|moderate|high|critical

    pharmacogenomics = db.Column(db.Text(), nullable=True)  # JSON string
    clinical_recommendations = db.Column(db.Text(), nullable=True)  # JSON string
    llm_explanation = db.Column(db.Text(), nullable=True)  # JSON string
    quality_metrics = db.Column(db.Text(), nullable=True)  # JSON string

    status = db.Column(db.String(20), default='pending')
