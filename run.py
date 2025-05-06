from app import create_app
from app.extensions import db
from app.models import User
from app import models
from flask_migrate import Migrate

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        migrate = Migrate(app, db)
        db.create_all()  # Not strictly necessary once using Migrate
    app.run(debug=True)