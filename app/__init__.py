from flask import Flask, render_template
from flask_login import current_user
import logging
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Import and initialize extensions here
    from app.extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints here
    from app.routes.user import user
    app.register_blueprint(user)

    app.config['SECRET_KEY'] = 'password' # CHANGE THIS TO SOMETHING MORE SECURE BEFORE PUSHING APP LIVE  
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    app.logger.debug(f"Registered blueprints: {app.blueprints}")

    @app.route('/')
    def index():
        app.logger.debug(f'Stuff: {current_user.is_authenticated}')
        if current_user.is_authenticated:
            app.logger.debug(f'User authenticated: {current_user.username}')
        return render_template('public/index.html')

    @app.route('/about')
    def about():
        return render_template('public/about.html')

    @app.route('/contact')
    def contact():
        return render_template('public/contact.html')    

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User, Admin

        if user_id == '0':
            return Admin(0)
        else:
            return db.session.execute(
                db.select(User).where(User.id == user_id)
            ).scalar()
    
    return app
