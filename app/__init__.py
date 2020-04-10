from flask import Flask, redirect, url_for, flash
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_migrate import Migrate, MigrateCommand
from flask_user import UserManager
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager
import pytz
from .quiz_generator import nltk_downloader

csrf_protect = CSRFProtect()
db = SQLAlchemy()
mail = Mail()
migrate = Migrate()
login_manager = LoginManager()
local_timezone = pytz.timezone('Asia/Jakarta')



def register_all_blueprints(app):
    """
    Register all each blueprints for each modules (auth, admin, student)
    """
    from .routes import main_bp
    from .auth.routes import auth_bp
    from .admin.routes import admin_bp
    from .student.routes import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(main_bp)

    return app



def create_app(extra_config_settings={}):

    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object('app.settings')
    app.config.from_object('app.local_settings')
    app.config.update(extra_config_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    # mail.init_app(app)
    csrf_protect.init_app(app)
    login_manager.init_app(app)


    from wtforms.fields import HiddenField
    def is_hidden_field_filter(field):
        return isinstance(field, HiddenField)

    with app.app_context():
        app = register_all_blueprints(app)
        db.create_all()

    from .models import User
    user_manager = UserManager(app, db, User)
    

    @app.context_processor
    def context_processor():
        def local_time(utc):
            local = utc.astimezone(local_timezone)
            return local.strftime('%B %d, %Y %X %Z')

        return dict(user_manager=user_manager, local_time=local_time, hasattr=hasattr)


    return app


def init_email_error_handler(app):
    """
    Initialize a logger to send emails on error-level messages.
    Unhandled exceptions will now send an email message to app.config.ADMINS.
    """
    if app.debug: return  # Do not send error emails while developing

    # Retrieve email settings from app.config
    host = app.config['MAIL_SERVER']
    port = app.config['MAIL_PORT']
    from_addr = app.config['MAIL_DEFAULT_SENDER']
    username = app.config['MAIL_USERNAME']
    password = app.config['MAIL_PASSWORD']
    secure = () if app.config.get('MAIL_USE_TLS') else None

    # Retrieve app settings from app.config
    to_addr_list = app.config['ADMINS']
    subject = app.config.get('APP_SYSTEM_ERROR_SUBJECT_LINE', 'System Error')

    # Setup an SMTP mail handler for error-level messages
    import logging
    from logging.handlers import SMTPHandler

    mail_handler = SMTPHandler(
        mailhost=(host, port),  # Mail host and port
        fromaddr=from_addr,  # From address
        toaddrs=to_addr_list,  # To address
        subject=subject,  # Subject line
        credentials=(username, password),  # Credentials
        secure=secure,
    )
    mail_handler.setLevel(logging.ERROR)
    app.logger.addHandler(mail_handler)
