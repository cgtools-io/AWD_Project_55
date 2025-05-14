from flask import Flask, render_template, abort
from flask_login import current_user
import logging
from config import Config
import app.constants as msg

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)
    print("DB in use:", app.config["SQLALCHEMY_DATABASE_URI"]) # Debugging multiple db issues

    # Import and initialize extensions here
    from app.extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # To redirect with a flash message instead of ERROR page
    @login_manager.unauthorized_handler
    def custom_unauthorized():
        # Forces a 403 error instead of redirecting to login page
        return abort(403)

    login_manager.login_view = 'user.login'
    login_manager.login_message = msg.LOGIN_REQUIRED
    login_manager.login_message_category = "danger"

    # Error handlers
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return render_template('errors/401.html'), 401

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return render_template('errors/405.html'), 405

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

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

    @app.route('/dashboard')
    def dashboard():
        return render_template('user/dashboard.html')
    
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
