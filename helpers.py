from nba_api.stats.endpoints import commonallplayers
import pandas as pd
from werkzeug.security import generate_password_hash, check_password_hash
import re


def load_player_list():
    # Request all players. Set LeagueID='00' for NBA, Season='current' gives full history.
    players = commonallplayers.CommonAllPlayers(is_only_current_season=0).get_data_frames()[0]

    # Convert to DataFrame
    df = pd.DataFrame(players)

    # If you want just a list of names:
    return (df['DISPLAY_FIRST_LAST'].tolist())
    


def check_login():
    if session['id']:
        return True
    return False

def hash_pass(password):
    return generate_password_hash(password)


def validate_password(password):
    if len(password) < 8:
        return "Password must have be at least 8 characters."
        
    if not re.search(r'[a-z]', password):
        return "Password must contain a lowercase letter."

    if not re.search(r'[A-Z]', password):
        return "Password must contain an uppercase letter."

    if not re.search(r'\d', password):
        return "Password must contain a digit."

    if not re.search(r'[@$!%*?&]', password): # Example special characters
        return "Password must contain a special character (@$!%*?&)."

    if re.search(r'\s', password): # Check for spaces (should not have any)
        return "Password cannot contain any spaces."

