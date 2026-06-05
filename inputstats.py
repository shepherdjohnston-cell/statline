from app import app, db, Statline, Clues
from flask_sqlalchemy import SQLAlchemy
import re

#Todo: add more error checking
def main():

    #clues table
    teams = input("Teams: ")
    if not re.fullmatch(r"[A-Z]{1}[a-z]+ vs. [A-Z]{1}[a-z]+", teams):
        return
    
    gameDate = input("Gamedate: ")
    if not re.fullmatch(r"\d{2}-\d{2}-\d{2}", gameDate):
        return
    
    yearDrafted = input("Year Drafted: ")
    if not re.fullmatch(r"\d{4}", yearDrafted):
        return



    #statline table
    player = input("player: ")
    if not re.fullmatch(r"[A-Z]{1}[a-z]+ [A-Z]{1}[a-z]+", player):
        return


    numberNames = ["pts", "reb", "ast", "stl", "blk", "to"]
    numberStats = {}
    for stat in numberNames:
        try:
            numberStats[stat] = int(input(f"{stat}: "))
        except ValueError:
            print("invalid input")
            return

    
    fractionStatsNames = ["fg", "threePoint", "ft"]
    fractionStats = {}
    for stat in fractionStatsNames:
        fractionStats[stat] = input(f"{stat}: ")
        if not re.fullmatch(r"^\d+/\d+$", fractionStats[stat]):
            return

    #create statline entry
    statline = Statline(player=player, pts=numberStats["pts"], reb=numberStats["reb"], ast=numberStats["ast"], stl=numberStats["stl"], blk=numberStats["blk"], to=numberStats["to"], fg=fractionStats["fg"], threePoint=fractionStats["threePoint"], ft=fractionStats["ft"])
    

    
    #append clues
    clues = Clues(teams=teams, gameDate=gameDate, yearDrafted=yearDrafted)
    statline.clues.append(clues)

    #commit
    db.session.add(statline)
    db.session.commit()


    

    

if __name__=="__main__":
    with app.app_context():
        main()
