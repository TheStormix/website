from flask import Flask
from flask_mail import Mail
from dotenv import load_dotenv
import os
from pathlib import Path
mail = Mail()

def create_app():
    
    load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env')

    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key_here')

    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

    mail.init_app(app)

    from app.routes import main, auth, admin, user
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(user.bp)

    from app.utils.db import init_db
    init_db()

    return app


