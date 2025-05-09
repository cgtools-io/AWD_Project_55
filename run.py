from app import create_app
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
    # DO NOT UNCOMMENT WHEN PUSHING TO MAIN OR OPENING A PR   
    # ========================================================
    app.run(debug=True)
