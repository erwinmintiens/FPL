import json
import os
import configparser
import sqlite3


def setup():
    config = configparser.ConfigParser()
    if os.path.exists('conf/config.ini'):
        config.read('conf/config.ini')
    else:
        if not os.path.exists('conf'):
            os.makedirs('conf')

        config["settings"] = {
            "current_season": '2021'
        }
        config["players"] = {
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
        with open('conf/config.ini', 'w') as configfile:
            config.write(configfile)

    if not os.path.exists(config["settings"]["current_season"]):
        os.makedirs(config["settings"]["current_season"])
    if not os.path.exists(config["settings"]["current_season"] + "/data"):
        os.makedirs(config["settings"]["current_season"] + "/data")
    if not os.path.exists(config["settings"]["current_season"] + "/data/gameweek_history"):
        os.makedirs(config["settings"]["current_season"] + "/data/gameweek_history")
    for i in range(1, 39):
        if not os.path.exists(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(i) + ".json"):
            with open(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(i) + ".json", "w") as file:
                file.write("[]")


setup()
