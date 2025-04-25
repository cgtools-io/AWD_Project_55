from flask import Flask, render_template, url_for
from flask_login import LoginManager, current_user
import logging

def create_app(config_name="development"):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    # from .routes.user import user
    # app.register_blueprint(user)

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
    
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # login_manager.login_view = 'auth.login'

    # @login_manager.user_loader
    # def load_user(user_id):
    #     from .models import User
    #     return User.query.get(int(user_id))
    
    
    return app