from helpers import check_login, load_player_list, hash_pass, validate_password
from flask import Flask, render_template, jsonify, request, session, redirect
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import re
from sqlalchemy.exc import IntegrityError
from werkzeug.security import check_password_hash


app = Flask(__name__)


#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///statline.sqlite3'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password123@localhost/statline1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'statline_key'

db = SQLAlchemy(app)

migrate = Migrate(app,db)

#model for statline and player
class Statline(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player = db.Column(db.String(30), nullable=False)
    pts = db.Column(db.Integer, nullable=False)
    reb = db.Column(db.Integer, nullable=False)
    ast = db.Column(db.Integer, nullable=False)
    stl = db.Column(db.Integer, nullable=False)
    blk = db.Column(db.Integer, nullable=False)
    to = db.Column(db.Integer, nullable=False)
    fg = db.Column(db.String(5), nullable=False)
    threePoint = db.Column(db.String(5), nullable=False)
    ft = db.Column(db.String(5), nullable=False)

    clues = db.relationship("Clues", back_populates="statline", cascade="all, delete-orphan")
    stats = db.relationship("Stats", back_populates="statline", cascade="all, delete-orphan")


#model for clues
class Clues(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    statline_id = db.Column(db.Integer, db.ForeignKey("statline.id"), nullable=False)

    teams = db.Column(db.String(50), nullable=False)
    gameDate = db.Column(db.String(15), nullable=False)
    yearDrafted = db.Column(db.String(4), nullable=False)
    
    statline = db.relationship("Statline", back_populates="clues")

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    hash = db.Column(db.String(255), nullable=False)

    stats = db.relationship("Stats", back_populates="users", cascade="all, delete-orphan")

class Stats(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    statline_id = db.Column(db.Integer, db.ForeignKey("statline.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    game_won = db.Column(db.Boolean, nullable=False)

    guesses = db.Column(db.Integer, nullable=False)
    hints = db.Column(db.Integer, nullable=False)

    statline = db.relationship("Statline", back_populates="stats")
    users = db.relationship("Users", back_populates="stats")
    

#globals
player_list = [] #for auto-complete player list
elapsed_days = 1#temporary
current_day = 2 #temporary hard coding

def startup(): #runs once every time server starts
    global player_list, current_day, elapsed_days 
    print("Loading player list...")
    player_list = load_player_list() #failsafe for intial startup 
    print("Players Loaded:", len(player_list))
    with app.app_context():
        db.create_all()

with app.app_context():
    startup()




@app.context_processor
def login_box():
    return dict(
        user_logged_in=("user_id" in session)
    )


@app.route("/")
@app.route("/archive/game")
def index():

    day = request.args.get("day", type=int)

    if day is None or day > get_current_day():
        day = get_current_day()

    stat = Statline.query.filter_by(id = day).first()

    stats = [
        stat.pts, stat.reb, stat.ast, stat.stl, stat.blk,
        stat.to, stat.fg, stat.threePoint, stat.ft
    ]

    clue = Statline.query.filter_by(id = day).first().clues[0]
    clues = {"Teams":clue.teams, "Game Date":clue.gameDate, "Year Drafted":clue.yearDrafted}

    return render_template("index.html", clues=clues, stats=stats, day=day)

@app.route("/api/players")
def players():
    return jsonify(player_list) #fufills javascript promise

@app.route("/api/stats", methods=['POST'])
def stats():
    if "user_id" not in session: #if user isnt logged in stats dont get saved
        return jsonify({"status": "not_logged_in"})

    data = request.get_json() #backend sends json when game is completed

    day = data.get('day')
    if day is None:
        return jsonify({"error": "Missing day"}), 400

    if Stats.query.filter_by(statline_id=day, user_id=session["user_id"]).first(): #checks for repeat submission on the same day
        return jsonify({"status": "Repeat submission"})

    
    guesses = data.get("guesses")
    if guesses is None:
        return jsonify({"error", "Missing guess count"}), 400

    hints = data.get("hints")
    if hints is None:
        return jsonify({"error", "Missing hint count"}), 400

    game_won = data.get("game_won")
    if game_won is None:
        return jsonify({"error", "Missing game status"}), 400


    stat = Stats(statline_id=day, user_id=session["user_id"], game_won=game_won, guesses=guesses, hints=hints) #adds to db object
    db.session.add(stat)
    db.session.commit()

    return jsonify({"status": "success"})

@app.route("/validate_guess", methods=['POST'])
def validate_guess():
    try:
        data = request.get_json() #corresponds to js fetch when submit button is pressed
        guess = data.get('guess', '').lower() #parses json for player name
        day = data.get('day')

        if day is None:
            return jsonify({"error": "Missing day"}), 400

        stat = Statline.query.filter_by(id=day).first()
        if not stat:
            return jsonify({"error": "Invalid day"}), 400

        correct_player = stat.player.lower()

        if guess not in [player.lower() for player in player_list]: 
            is_valid = -1 # -1 corresponds to invalid guess
        elif (guess == correct_player.lower()): 
            is_valid = 0 # 0 corresponds to correct player
        else: 
            is_valid = 1 #1 orresponds to valid guess, but not correct

        return jsonify({"valid": is_valid}) #fufills javascript promise

    except Exception as e: # catches all exceptions
        print("Error:", e)
        #TODO call apon error page function
        return jsonify({"error": str(e)}), 500

@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        #data from submmited from html form
        username = request.form.get('username').strip()
        password = request.form.get('password')
        
        
        user = Users.query.filter_by(username=username).first() #intializes user structure from database

        if not user or not check_password_hash(user.hash, password): #user will equal none if username doesnt exist
            return render_template("login.html", error="Invalid username or password")
        
        session['user_id'] = user.id #sets session id if login is succesfull
        session.permanent = True

        return redirect("/")
    
    return render_template("login.html")

@app.route("/signup", methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':

        #data from form
        username = request.form.get('username').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

    
        #password checking
        if password != confirm_password:
            return render_template("signup.html", error="Passwords do not match.")

        error = validate_password(password)
        
        if error:
            return render_template("signup.html", error=error)

        
        #username checking
        if Users.query.filter_by(username=username).first():
            return render_template("signup.html", error="Username already in use")
        
        if len(username) > 45:
            return render_template("signup.html", error="Username must be 45 characters or less")
        
        if not re.match(r"^\w*$", username):
            return render_template("signup.html", error="Username must only contain '0-9', 'a-Z', or '_'")
        
        hash = hash_pass(password)
        user = Users(username=username, hash=hash)

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            return render_template("signup.html", error="Username already in use")
        
        session['user_id'] = user.id
        session.permanent = True
        print("User created:", username)

        return redirect("/")
        
    return render_template("signup.html")

@app.route("/logout", methods=['GET'])
def logout():
    session.pop("user_id", None)
    return redirect("/")

@app.route("/userstats", methods=['GET'])
def userstats():
    if "user_id" not in session:
        return render_template("login.html", error="Login to track stats.")

    stats = Stats.query.filter_by(user_id=session["user_id"]).all()

    total_guesses = 0
    total_hints = 0
    total_games = 0
    total_win = 0

    for s in stats:
        total_guesses += s.guesses
        total_hints += s.hints
        total_games += 1
        total_win += s.game_won

    if not total_games:
        return render_template("userstats.html", avg_guesses=0, avg_hints=0, win_per=0) 
    avg_guesses = total_guesses / total_games
    avg_hints = total_hints / total_games
    win_per = 100 * (total_win / total_games)

    return render_template("userstats.html", stats=stats, avg_guesses=avg_guesses, avg_hints=avg_hints, win_per=win_per) 

@app.route("/archive", methods=['GET'])
def archive():
    global current_day

    days = current_day #size of archive

    return render_template("archive.html", days=days) #render archive page, with number of days


def get_current_day():
    #day Loader
    global player_list, current_day
    if current_day != (elapsed_days + 1): #is only true for the first user to visit website on a given day\
        player_list = load_player_list()
        current_day = (elapsed_days + 1)
    
    return current_day