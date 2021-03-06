import configparser
import json
import os

import fpl_api
import __init__
from typing import Union
# import info

config = configparser.ConfigParser()
config.read('conf/config.ini')


def fetch_all_latest_info():
    print("Getting FPL managers...")
    get_all_person_data_and_save_to_json()
    print("Getting GW results per player...")
    get_entire_gameweek_results_per_player_and_save()
    print("Getting all player properties...")
    get_entire_player_properties_and_save()
    print("Getting teams info...")
    get_all_team_info_and_save()
    print("Get gameweeks...")
    get_finished_gameweeks_and_save()
    print("Get fixtures...")
    get_all_fixtures_and_save()
    print("Getting bootstrap_static...")
    get_bootstrap_static_and_save()


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


def get_all_person_data_and_save_to_json():
    conn = fpl_api.FPLCalls()
    event_status_call = conn.get_event_status()
    if event_status_call.status_code != 200:
        return
    event_status = json.loads(event_status_call.text)
    if event_status["leagues"] == "Updated":
        previous_gameweek = event_status["status"][0]["event"]
    else:
        previous_gameweek = event_status["status"][0]["event"] - 1
    for person_name, person_id in config["managers"].items():
        gw_history = list()
        for item in range(1, previous_gameweek + 1):
            result_call = conn.get_person_picks(person_id, item)
            result = json.loads(result_call.text)
            gw_history.append(result)
        with open(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json", 'w') as outfile:
            outfile.write(json.dumps(gw_history))


def update_persons_jsons(fpl_connection: fpl_api.FPLCalls):
    event_status_call = conn.get_event_status()
    if event_status_call.status_code != 200:
        return
    event_status = json.loads(event_status_call.text)
    if event_status["leagues"] == "Updated":
        previous_gameweek = event_status["status"][0]["event"]
    else:
        previous_gameweek = event_status["status"][0]["event"] - 1
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
            with open(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(json_file))
        else:
            gw_history = dict()
            for item in range(1, previous_gameweek + 1):
                result_call = fpl_connection.get_person_picks(person_id, item)
                result = json.loads(result_call.text)
                gw_history[item] = result
            with open(config["settings"]["current_season"] + "/data/managers/" + person_name + "_" + person_id + ".json",
                      'w') as outfile:
                outfile.write(json.dumps(gw_history))


def get_entire_gameweek_results_per_player_and_save():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)

    event_status_call = conn.get_event_status()
    if event_status_call.status_code != 200:
        return
    event_status = json.loads(event_status_call.text)
    if event_status["leagues"] == "Updated":
        previous_gameweek = event_status["status"][0]["event"]
    else:
        previous_gameweek = event_status["status"][0]["event"] - 1


    for player in bootstrap_static["elements"]:
        print("Player", player["id"])
        player_summary_call = conn.get_player_summary(player["id"])
        if player_summary_call.status_code != 200:
            return
        player_summary = json.loads(player_summary_call.text)
        for gw in player_summary["history"]:
            with open(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(gw["round"]) + ".json", "r") as file:
                gameweek_json = json.load(file)
            gameweek_json.append(gw)
            with open(config["settings"]["current_season"] + "/data/players/gameweek_history/gameweek_" + str(
                    gw["round"]) + ".json", "w") as file:
                file.write(json.dumps(gameweek_json))


def get_entire_player_properties_and_save():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)

    for player in bootstrap_static["elements"]:
        player_summary_call = conn.get_player_summary(player["id"])
        if player_summary_call.status_code != 200:
            return
        player_summary = json.loads(player_summary_call.text)
        print("Player", player["id"])
        with open(f"{config['settings']['current_season']}/data/players/{player['id']}_{player['web_name']}.json", "w") as file:
            file.write(json.dumps(player_summary["history"]))


def get_all_team_info_and_save():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)

    for team in bootstrap_static["teams"]:
        with open(config["settings"]["current_season"] + "/data/teams/" + str(team["id"]) + "_" + team["name"] + ".json", "w") as file:
            file.write(json.dumps(team))
    with open(config["settings"]["current_season"] + "/data/teams/all_teams.json", "w") as file:
        file.write(json.dumps(bootstrap_static["teams"]))


def get_finished_gameweeks_and_save():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)
    last_finished_gameweek = 0
    for gameweek in bootstrap_static["events"]:
        if gameweek["finished"] and gameweek["data_checked"]:
            with open(config["settings"]["current_season"] + "/data/gameweeks/general/gameweek_" + str(gameweek["id"]) + ".json", "w") as file:
                file.write(json.dumps(gameweek))
            if gameweek["id"] > last_finished_gameweek:
                last_finished_gameweek = gameweek["id"]
    config["settings"]["last_finished_gameweek"] = str(last_finished_gameweek)
    save_config()
    get_player_performances_and_save()


def get_player_performances_and_save():
    conn = fpl_api.FPLCalls()
    for gameweek in range(len(os.listdir(config["settings"]["current_season"] + "/data/gameweeks/general/"))):
        fixture_results_call = conn.get_live_player_stats(gameweek + 1)
        if fixture_results_call.status_code != 200:
            continue
        fixture_results = json.loads(fixture_results_call.text)
        with open(config["settings"]["current_season"] + "/data/gameweeks/player_performances/gameweek_" + str(gameweek + 1) + ".json", "w") as file:
            file.write(json.dumps(fixture_results))


def get_all_fixtures_and_save():
    conn = fpl_api.FPLCalls()
    fixtures_call = conn.get_fixtures(event=None, only_future_fixtures=False)
    if fixtures_call.status_code != 200:
        return
    fixtures = json.loads(fixtures_call.text)
    for fixture in fixtures:
        print(fixture["id"])
        if fixture["finished"]:
            with open(config["settings"]["current_season"] + "/data/fixtures/" + str(fixture["id"]) + "-" + str(fixture["team_h"]) + "_" + str(fixture["team_a"]) + "-finished" + ".json", "w") as file:
                file.write(json.dumps(fixture))
        else:
            with open(config["settings"]["current_season"] + "/data/fixtures/" + str(fixture["id"]) + "-" + str(fixture["team_h"]) + "_" + str(fixture["team_a"]) + ".json", "w") as file:
                file.write(json.dumps(fixture))


def get_bootstrap_static_and_save():
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)
    with open(f"{config['settings']['current_season']}/data/bootstrap_static.json", "w") as file:
        file.write(json.dumps(bootstrap_static))


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

    # fetch_all_latest_info()
    get_all_person_data_and_save_to_json()
    # get_all_team_info_and_save()
    # get_entire_player_properties_and_save()



