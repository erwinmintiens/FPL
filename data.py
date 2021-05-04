import configparser
import json
import os

import fpl_api
import __init__
from typing import Union

__init__.setup()

config = configparser.ConfigParser()
config.read('conf/config.ini')


def save_config():
    with open('conf/config.ini', 'w') as configfile:
        config.write(configfile)


def add_manager(manager_name: str, manager_id: Union[int, str]):
    if manager_name in config["managers"]:
        raise ValueError(f"Manager {manager_name} already present in config.ini")
    if str(manager_id) in config["managers"].values():
        raise ValueError(f"Manager ID {manager_id} already present in config.ini")
    config["managers"][manager_name] = str(manager_id)
    save_config()


def add_league(league_name: str, league_id: Union[int, str]):
    if league_name in config["leagues"]:
        raise ValueError(f"League name {league_name} already present in config.ini")
    if str(league_id) in config["leagues"].values():
        raise ValueError(f"League ID {league_id} already present in config.ini")
    config["leagues"][league_name] = str(league_id)
    save_config()


def delete_manager(manager_id: Union[int, str]):
    if str(manager_id) not in config["managers"].values():
        raise ValueError(f"Manager ID {manager_id} not found in config.ini")
    for name, value in config["managers"].items():
        if value == str(manager_id):
            del config["managers"][name]
            break
    save_config()


def delete_league(league_id: Union[int, str]):
    if str(league_id) not in config["leagues"].values():
        raise ValueError(f"League with ID {league_id} not found in config.ini")
    for name, value in config["leagues"].items():
        if value == str(league_id):
            del config["leagues"][name]
            break
    save_config()


def get_all_person_data_and_save_to_json(bootstrap_static_json, fpl_connection: fpl_api.FPLCalls):
    previous_gameweek = 0
    for gameweek in bootstrap_static_json["events"]:
        if gameweek["is_previous"]:
            previous_gameweek = gameweek["id"]
    for person_name, person_id in config["managers"].items():
        gw_history = list()
        for item in range(1, previous_gameweek + 1):
            result_call = fpl_connection.get_person_picks(person_id, item)
            result = json.loads(result_call.text)
            gw_history.append(result)
        with open(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json", 'w') as outfile:
            outfile.write(json.dumps(gw_history))


def update_persons_jsons(bootstrap_static_json, fpl_connection: fpl_api.FPLCalls):
    previous_gameweek = 0
    for gameweek in bootstrap_static_json["events"]:
        if gameweek["is_previous"]:
            previous_gameweek = gameweek["id"]
            print("Previous Gameweek:", previous_gameweek)
    for person_name, person_id in config["managers"].items():
        if os.path.exists(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json"):
            with open(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json") as file:
                json_file = json.load(file)
            gameweeks_in_json = len(json_file)
            print("Gameweeks found in json:", gameweeks_in_json)

            if previous_gameweek == gameweeks_in_json:
                continue
            for item in range(gameweeks_in_json + 1, previous_gameweek + 1):
                result_call = fpl_connection.get_person_picks(person_id, item)
                result = json.loads(result_call.text)
                json_file[item] = result
            with open(config["settings"]["current_season"] + "/data/managers" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(json_file))
        else:
            gw_history = dict()
            for item in range(1, previous_gameweek + 1):
                result_call = fpl_connection.get_person_picks(person_id, item)
                result = json.loads(result_call.text)
                gw_history[item] = result
            with open(config["settings"]["current_season"] + "/data/managers" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(gw_history))


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
    # captain_points = get_extra_captaincy_points_between_gws(conn, config["managers"]["erwin"], 25, 33)
    # print(sum(captain_points))

    # print(conn.get_person_picks(435872, 1))

    # get_all_person_data_and_save_to_json(bootstrap_static, conn)

    # update_persons_jsons(bootstrap_static, conn)

    # update_entire_player_database()
    delete_league(435851)



