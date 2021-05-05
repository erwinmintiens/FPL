import matplotlib as plt
import configparser
import __init__
import json
import os
# import fpl_api

__init__.setup()
config = configparser.ConfigParser()
config.read('conf/config.ini')


def generate_extra_captaincy_points_graph():
    total_y_axis = list()
    persons = list()
    for person_name, person_id in config["managers"].items():
        persons.append(person_name)
        y_axis = list()
        y_axis.append(person_name)
        if os.path.exists(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json"):
            with open(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json") as file:
                json_file = json.load(file)
            max_gw = 0
            for gw in json_file:
                if gw["entry_history"]["event"] > max_gw:
                    max_gw = gw["entry_history"]["event"]
            x_axis = list()
            for item in range(1, max_gw + 1):
                x_axis.append("GW" + str(item))
            for gameweek in json_file:
                points_this_gw = 0
                for player in gameweek["picks"]:
                    if player["is_captain"] and player["multiplier"] not in [0, "0", 1, "1"]:
                        if os.path.exists(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(gameweek["entry_history"]["event"]) + ".json"):
                            with open(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(gameweek["entry_history"]["event"]) + ".json") as file:
                                gameweek_json_file = json.load(file)
                            for item in gameweek_json_file:
                                if item["element"] == player["element"]:
                                    points_this_gw += item["total_points"]
                    elif player["is_captain"] and player["multiplier"] in [0, "0", 1, "1"]:
                        for player in gameweek["picks"]:
                            if player["is_vice_captain"] and player["multiplier"] not in [0, "0", 1, "1"]:
                                if os.path.exists(
                                        config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(
                                                gameweek["entry_history"]["event"]) + ".json"):
                                    with open(config["settings"][
                                                  "current_season"] + "/data/players/gameweek_history/gameweek_" + str(
                                            gameweek["entry_history"]["event"]) + ".json") as file:
                                        gameweek_json_file = json.load(file)
                                    for item in gameweek_json_file:
                                        if item["element"] == player["element"]:
                                            points_this_gw += item["total_points"]
                    else:
                        pass

                if gameweek["active_chip"] == "3xc":
                    print(points_this_gw * 2)
                    y_axis.append(points_this_gw * 2)
                else:
                    print(points_this_gw)
                    y_axis.append(points_this_gw)
        total_y_axis.append(y_axis)
    fig = plt.figure(figsize=(20, 10))
    # ax = fig.add_axes([0.05, 0.1, 0.9, 0.85])
    for i in range(len(total_y_axis)):
        plt.plot(x_axis, total_y_axis[i][1:])
    plt.legend(persons)
    plt.grid()
    plt.show()
    fig.savefig('captain_points.png')

    gameweek5, gameweek10, gameweek15, gameweek20, gameweek25, gameweek30, gameweek35, gameweek38 = list(), list(), list(), list(), list(), list(), list(), list()

    for element in total_y_axis:
        print(element)
        element.pop(0)
        gameweek5.append(sum(element[0:5]))
        gameweek10.append(sum(element[5:10]))
        gameweek15.append(sum(element[10:15]))
        gameweek20.append(sum(element[15:20]))
        gameweek25.append(sum(element[20:25]))
        gameweek30.append(sum(element[25:30]))
        gameweek35.append(sum(element[30:35]))
        gameweek38.append(sum(element[35:38]))
    print(gameweek5)

if __name__ == '__main__':
    pass
    # generate_extra_captaincy_points_graph()