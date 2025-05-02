from flask import Flask, render_template, url_for
from flask_login import LoginManager, current_user
import logging

def create_app(config_name="development"):
    app = Flask(__name__, static_folder='static', template_folder='templates')

    app.config['SECRET_KEY'] = 'password' # CHANGE THIS TO SOMETHING MORE SECURE BEFORE PUSHING APP LIVE  
    logging.basicConfig(level=logging.DEBUG)
    app.logger.setLevel(logging.DEBUG)

    from app.routes import upload  # To register our real file_upload() route
    # from .routes.user import user
    # app.register_blueprint(user)

    app.logger.debug(f"Registered blueprints: {app.blueprints}")

    @app.route('/')
    def index():
        return render_template('index.html')

    #Editing out the below while I troubleshoot getting Flask to run Forms
    #@app.route('/file_upload')
    #def file_upload():
    #    return render_template('user/file_upload.html')
    
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

    
    # login_manager = LoginManager()
    # login_manager.init_app(app)
    # login_manager.login_view = 'auth.login'

    # @login_manager.user_loader
    # def load_user(user_id):
    #     from .models import User
    #     return User.query.get(int(user_id))
    
    from app.routes.upload import upload_bp
    app.register_blueprint(upload_bp)

    return app
