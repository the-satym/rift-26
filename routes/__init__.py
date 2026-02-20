from .admin import admin_bp
from .auth import auth_bp
from .doc import doc_bp
from .includes import includes_bp
def registering_routes(app):
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(doc_bp)
    app.register_blueprint(includes_bp)


