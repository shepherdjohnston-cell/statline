# test_stats.py
from app import app, db, Stats  # import your app, db, and model

# Replace with the user ID you want to query
user_id = 1  # example, instead of session["user_id"]

with app.app_context():
    Stats.__table__.drop(db.engine)

    db.create_all()