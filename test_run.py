# test_run.py
from app import create_app
from app.extensions import db
from config import TestConfig

app = create_app(TestConfig)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(port=5000)  # same as Selenium's target