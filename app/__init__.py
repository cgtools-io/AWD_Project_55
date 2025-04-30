from flask import Flask, render_template
import logging
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(config_class)

    # Import and initialize extensions here
    from app.extensions import db, migrate, login_manager, csrf
    db.init_app(app)
    migrate.init_app(app, db)
    #login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints here
    # from app.routes.user import user
    # app.register_blueprint(user)

    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    app.logger.debug(f"Registered blueprints: {app.blueprints}")

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/file_upload')
    def file_upload():
        return render_template('user/file_upload.html')
    
    @app.route('/login')
    def login():
        return render_template('auth/login.html')
    
    @app.route('/signup')
    def signup():
        return render_template('auth/signup.html')

    @app.route('/about')
    def about():
        return render_template('about.html')

    @app.route('/contact')
    def contact():
        return render_template('contact.html')

    @app.route('/visual')
    def visual():
        return render_template('user/visual_v03.html')    
    
    return app
