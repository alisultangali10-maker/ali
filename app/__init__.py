from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from datetime import timedelta
import os

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = "Пожалуйста, войдите, чтобы получить доступ к этой странице."

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    
    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints
    from app.routes import main
    from app.admin import admin_bp
    
    app.register_blueprint(main)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Template context processors
    from app.translations import get_translation

    def to_kz_time(dt):
        if dt:
            return dt + timedelta(hours=5)
        return dt

    @app.context_processor
    def inject_translations():
        def _(key):
            lang = session.get('lang', 'ru')
            return get_translation(lang, key)
        return dict(
            _=_,
            current_lang=lambda: session.get('lang', 'ru'),
            to_kz_time=to_kz_time
        )
        
    with app.app_context():
        db.create_all()
    
    return app
