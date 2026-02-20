from flask import Blueprint, render_template, session
from models import Users, db
from werkzeug.security import generate_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/super-admin')

def create_default_admin():
    admin=Users.query.filter_by(user_type="super-admin").first()

    if not admin:
        new_admin=Users(
            user_type = "super-admin",
            email="connect.satym@gmail.com",
            password_hash=generate_password_hash("admin-123"),
            phone=9569802669,
            is_active=True
        )
        db.session.add(new_admin)
        db.session.commit()
        print("admin created")

@admin_bp.route('dashboard')
def dashboard():
    if session.get('user_type') == "super-admin":
        pass
    else:
        return "Unauthorized", 403
    return render_template('dashboard/admin_dash.html')