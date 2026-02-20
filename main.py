from flask import Flask
from routes import registering_routes
from models import *
import config
from routes.admin import create_default_admin

app=Flask(__name__)
app.config['SECRET_KEY']= config.secret_key
app.config['SQLALCHEMY_DATABASE_URI']= config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= config.SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)



with app.app_context():
    db.create_all()
    create_default_admin()

registering_routes(app)

@app.after_request
def add_nocache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5001)