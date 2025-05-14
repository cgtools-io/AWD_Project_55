from app import create_app, models
from app.extensions import db
from app.models import User
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist

    # ========================================================
    # DEBUG MODE — DEVELOPMENT USE ONLY                       
    # ========================================================
    app.run(debug=True)
