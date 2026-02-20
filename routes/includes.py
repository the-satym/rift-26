from flask import Flask, Blueprint,render_template

includes_bp = Blueprint('includes', __name__)

@includes_bp.route('/', methods=['GET', 'POST'])
def index():
    return render_template('includes/index.html')