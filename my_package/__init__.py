from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
from sqlalchemy import MetaData

UPLOAD_FOLDER = os.path.join('my_package/static/css', 'csv')

ALLOWED_EXTENSIONS = {'csv'}

db = SQLAlchemy()
DB_NAME = "database.db"
metadata = MetaData()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'hjshjhdjah kjshkjdhjs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    db.init_app(app)

    with app.app_context():
        from my_package.models import User, CRM  # Move the import statement here
        create_database(app)

    from .views import views  # Replace '.' with the name of your project if needed
    from .auth import auth  # Replace '.' with the name of your project if needed

    app.register_blueprint(views, url_prefix='/views')
    app.register_blueprint(auth, url_prefix='/auth')

    return app

def create_database(app):
    if not path.exists(f'{DB_NAME}'):
        with app.app_context():
            metadata.create_all(db.engine)
            db.create_all()
        print('Created Database!')
