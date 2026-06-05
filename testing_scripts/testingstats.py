# test_stats.py
from app import app, db, Stats, Statline  # import your app, db, and model

# Replace with the user ID you want to query
user_id = 1  # example, instead of session["user_id"]

with app.app_context():
    stats_list = Statline.query.all()

    for s in stats_list:
        print(s.player)