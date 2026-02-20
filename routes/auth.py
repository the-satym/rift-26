

from flask import Flask, Blueprint, render_template, request, session, redirect,url_for, flash
from sqlalchemy import or_
from werkzeug.security import check_password_hash, generate_password_hash
from models import Users, Doc, Analysis
from models import Users, Doc, db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/doctor/signup', methods=['GET', 'POST'])
def doc_signup():
    if request.method == 'POST':
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        name = request.form.get('name')

        if password != confirm:
            flash("Passwords do not match.", "error")
            return render_template('auth/doc_signup.html')

        new_user = Users(
            user_type='doctor',
            email=email,
            password_hash=generate_password_hash(password),
            phone=phone,
            is_active=True,
        )
        db.session.add(new_user)
        db.session.flush()

        doc_info = Doc(
            user_id=new_user.user_id,
            name=name)
        db.session.add(doc_info)
        db.session.commit()

        flash("Doctor registered successfully. Please log in.", "success")
        return redirect(url_for('auth.doc_login'))

    return render_template('auth/doc_signup.html')
def generate_patient_id():
    last_patient = Analysis.query.order_by(Analysis.pat_id.desc()).first()
    if not last_patient:
        return "patient_001"

    last_num = int(last_patient.id.split("_")[1])
    new_num = last_num + 1

    # Automatically increase digit length as needed
    digits = max(3, len(str(new_num)))
    return f"patient_{new_num:0{digits}d}"

@auth_bp.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    return handle_login('super-admin','auth/admin_login.html')

@auth_bp.route('/doctor/login', methods=['GET', 'POST'])
def doc_login():
    return handle_login('doctor','auth/doc_login.html')

def handle_login(expected_role, template):
    if request.method == "POST":
        login_id = request.form.get("phone")
        password = request.form.get("password")

        user = Users.query.filter(or_(Users.phone == login_id, Users.email == login_id)).first()

        if user and check_password_hash(user.password_hash, password):
            if user.user_type == expected_role:
                session["user_id"] = user.user_id
                session["user_type"] = user.user_type

                if user.user_type == "super-admin":
                    return redirect(url_for("admin.dashboard"))
                elif user.user_type == "doctor":
                    return redirect(url_for("doc.dashboard"))
            else:
                flash("Unauthorized access for this role.", "danger")
                return render_template(template)
        else:
            flash("Invalid phone/email or password.", "danger")
            return render_template(template)
    return render_template(template)


@auth_bp.route('/logout')
def logout():
    usertype=session.get('user_type')
    if usertype=='super-admin':
        return handle_logout('auth.admin_login')
    elif usertype=='doctor':
        return handle_logout('auth.doc_login')

def handle_logout(template):
    session.clear()
    return redirect(url_for(template))

