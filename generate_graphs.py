import configparser
import json
import os

import fpl_api
import matplotlib.pyplot as plt
# import numpy as np
import __init__
from typing import Union
import pandas as pd

__init__.setup()

config = configparser.ConfigParser()
config.read('conf/config.ini')


def player_id_to_name(bootstrap_static_json, player_id: Union[int, str]):
    for item in bootstrap_static_json["elements"]:
        if item["id"] == player_id:
            return item["web_name"]
    return None


def player_web_name_to_id(bootstrap_static_json, web_name: str):
    for item in bootstrap_static_json["elements"]:
        if item["web_name"] == web_name:
            return item["id"]
    return None


def get_person_captain_for_gameweek(fpl_connection: fpl_api.FPLCalls, person_id: Union[int, str], gameweek: Union[int, str]):
    captain_played = False
    vice_captain_played = False
    is_triple_captain = False
    person_picks_call = fpl_connection.get_person_picks(person_id, gameweek)
    if person_picks_call.status_code != 200:
        return
    person_picks = json.loads(person_picks_call.text)
    for player in person_picks["picks"]:
        if player["is_captain"] and player["multiplier"] not in [0, 1]:
            if player["multiplier"] == 3:
                is_triple_captain = True
            captain_played = True
            return [player["element"], captain_played, vice_captain_played, is_triple_captain]
        if player["is_vice_captain"] and player["multiplier"] not in [0, 1]:
            if player["multiplier"] == 3:
                is_triple_captain = True
            vice_captain_played = True
            return [player["element"], captain_played, vice_captain_played, is_triple_captain]
    return [None, captain_played, vice_captain_played, is_triple_captain]


def get_points_for_player(fpl_connection: fpl_api.FPLCalls, player_id: Union[int, str], gameweek: Union[int, str]):
    player_summary_call = fpl_connection.get_player_summary(player_id)
    if player_summary_call.status_code != 200:
        return
    total = 0
    player_summary = json.loads(player_summary_call.text)
    for gw in player_summary["history"]:
        if gw["round"] == gameweek:
            total += gw["total_points"]
    return total


def get_extra_captaincy_points_between_gws(fpl_connection: fpl_api.FPLCalls, person_id: Union[int, str], lower_gw: Union[int, str], upper_gw: Union[int, str]):
    result = list()
    for gameweek in range(lower_gw, upper_gw + 1):
        captain = get_person_captain_for_gameweek(fpl_connection, person_id, gameweek)
        if type(captain) is list:
            if captain[0] is not None:
                if captain[3]:
                    result.append(get_points_for_player(fpl_connection, captain[0], gameweek) * 2)
                else:
                    result.append(get_points_for_player(fpl_connection, captain[0], gameweek))
            else:
                result.append(0)
        else:
            return
    return result


def get_all_person_data_and_save_to_json(bootstrap_static_json, fpl_connection: fpl_api.FPLCalls):
    previous_gameweek = 0
    for gameweek in bootstrap_static_json["events"]:
        if gameweek["is_previous"]:
            previous_gameweek = gameweek["id"]
    for person_name, person_id in config["players"].items():
        gw_history = list()
        for item in range(1, previous_gameweek + 1):
            result_call = fpl_connection.get_person_picks(person_id, item)
            result = json.loads(result_call.text)
            gw_history.append(result)
        with open(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json", 'w') as outfile:
            outfile.write(json.dumps(gw_history))


def update_persons_jsons(bootstrap_static_json, fpl_connection: fpl_api.FPLCalls):
    previous_gameweek = 0
    for gameweek in bootstrap_static_json["events"]:
        if gameweek["is_previous"]:
            previous_gameweek = gameweek["id"]
            print("Previous Gameweek", previous_gameweek)
    for person_name, person_id in config["players"].items():
        if os.path.exists(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json"):
            with open(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json") as file:
                json_file = json.load(file)
            gameweeks_in_json = list(map(int, json_file.keys()))

            if previous_gameweek == max(gameweeks_in_json):
                continue
            for item in range(max(gameweeks_in_json) + 1, previous_gameweek + 1):
                result_call = fpl_connection.get_person_picks(person_id, item)
                result = json.loads(result_call.text)
                json_file[item] = result
            with open(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(json_file))
        else:
            gw_history = dict()
            for item in range(1, previous_gameweek + 1):
                result_call = fpl_connection.get_person_picks(person_id, item)
                result = json.loads(result_call.text)
                gw_history[item] = result
            with open(config["settings"]["current_season"] + "/data/" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(gw_history))


def generate_extra_captaincy_points_graph():
    total_y_axis = list()
    persons = list()
    for person_name, person_id in config["players"].items():
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
                        if os.path.exists(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(gameweek["entry_history"]["event"]) + ".json"):
                            with open(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(gameweek["entry_history"]["event"]) + ".json") as file:
                                gameweek_json_file = json.load(file)
                            for item in gameweek_json_file:
                                if item["element"] == player["element"]:
                                    points_this_gw += item["total_points"]
                    elif player["is_captain"] and player["multiplier"] in [0, "0", 1, "1"]:
                        for player in gameweek["picks"]:
                            if player["is_vice_captain"] and player["multiplier"] not in [0, "0", 1, "1"]:
                                if os.path.exists(
                                        config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(
                                                gameweek["entry_history"]["event"]) + ".json"):
                                    with open(config["settings"][
                                                  "current_season"] + "/data/gameweek_history/gameweek_" + str(
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


def update_entire_player_database():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)

    for event in bootstrap_static["events"]:
        if event["finished"] and event["is_previous"]:
            last_gw = event["id"]

    for player in bootstrap_static["elements"]:
        print("Player", player["id"])
        player_summary_call = conn.get_player_summary(player["id"])
        if player_summary_call.status_code != 200:
            return
        player_summary = json.loads(player_summary_call.text)
        for gw in player_summary["history"]:
            with open(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(gw["round"]) + ".json", "r") as file:
                gameweek_json = json.load(file)
            gameweek_json.append(gw)
            with open(config["settings"]["current_season"] + "/data/gameweek_history/gameweek_" + str(
                    gw["round"]) + ".json", "w") as file:
                file.write(json.dumps(gameweek_json))


if __name__ == '__main__':

    conn = fpl_api.FPLCalls()

    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        exit()
    bootstrap_static = json.loads(bootstrap_static_call.text)


    # for gameweek in range(25, 34):
    #     y1 = list()
    #     x1 = list()
    #     for person in persons:
    #         captain = get_person_captain_for_gameweek(conn, person["id"], gameweek)
    #         print(captain)
    #         y1.append(get_points_for_player(conn, captain, gameweek))
    #
    #     x1.append("GW" + str(gameweek))
    #
    #     plt.plot(x1, y1)
    #     plt.show()
    #     exit()

    # print(get_person_captain_for_gameweek(conn, 1986671, 25))
    # print(get_points_for_player(conn, 570, 25))
    #
    # captain_points = get_extra_captaincy_points_between_gws(conn, config["players"]["erwin"], 25, 33)
    # print(sum(captain_points))

    # print(conn.get_person_picks(435872, 1))

    # get_all_person_data_and_save_to_json(bootstrap_static, conn)

    # update_persons_jsons(bootstrap_static, conn)

    update_entire_player_database()
    # generate_extra_captaincy_points_graph()


