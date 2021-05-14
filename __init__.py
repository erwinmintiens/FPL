import os
import configparser


config = configparser.ConfigParser()
if os.path.exists('conf/config.ini'):
    config.read('conf/config.ini')
else:
    if not os.path.exists('conf'):
        os.makedirs('conf')

    config["settings"] = {
        "current_season": '2021',
        "current_gameweek": 1
    }
    config["managers"] = {
        "arthur": "435872",
        "louis": "412783",
        "erwin": "1986671",
        "pieter": "4410825",
        "gert": "3992968",
        "michiel": "4440492",
        "wouter": "3126551",
        "stijn": "3725741",
        "niels": "578815"
    }
    config["leagues"] = {}
    with open('conf/config.ini', 'w') as configfile:
        config.write(configfile)

if not os.path.exists(config["settings"]["current_season"]):
    os.makedirs(config["settings"]["current_season"])
if not os.path.exists(config["settings"]["current_season"] + "/data"):
    os.makedirs(config["settings"]["current_season"] + "/data")
if not os.path.exists(config["settings"]["current_season"] + "/data/managers"):
    os.makedirs(config["settings"]["current_season"] + "/data/managers")
if not os.path.exists(config["settings"]["current_season"] + "/data/players"):
    os.makedirs(config["settings"]["current_season"] + "/data/players")
if not os.path.exists(config["settings"]["current_season"] + "/data/players/gameweek_history"):
    os.makedirs(config["settings"]["current_season"] + "/data/players/gameweek_history")
if not os.path.exists(config["settings"]["current_season"] + "/data/teams"):
    os.makedirs(config["settings"]["current_season"] + "/data/teams")
if not os.path.exists(config["settings"]["current_season"] + "/data/gameweeks"):
    os.makedirs(config["settings"]["current_season"] + "/data/gameweeks")
if not os.path.exists(config["settings"]["current_season"] + "/data/gameweeks/general"):
    os.makedirs(config["settings"]["current_season"] + "/data/gameweeks/general")
if not os.path.exists(config["settings"]["current_season"] + "/data/gameweeks/player_performances"):
    os.makedirs(config["settings"]["current_season"] + "/data/gameweeks/player_performances")
if not os.path.exists(config["settings"]["current_season"] + "/data/fixtures"):
    os.makedirs(config["settings"]["current_season"] + "/data/fixtures")
for i in range(1, 39):
    if not os.path.exists(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(i) + ".json"):
        with open(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(i) + ".json", "w") as file:
            file.write("[]")
