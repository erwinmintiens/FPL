from typing import Union
import fpl_api
import json


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


def get_player_points_per_minute(fpl_connection: fpl_api.FPLCalls, player_id: Union[int, str]):
    player_info_call = fpl_connection.get_player_summary(player_id)
    if player_info_call.status_code != 200:
        return
    player_info = json.loads(player_info_call.text)
    minutes = 0
    points = 0
    for game in player_info["history"]:
        minutes += game["minutes"]
        points += game["total_points"]
    return points/minutes


def get_player_points_per_90_minutes(fpl_connection: fpl_api.FPLCalls, player_id: Union[int, str]):
    ppm = get_player_points_per_minute(fpl_connection, player_id)
    return ppm * 90


if __name__ == '__main__':
    conn = fpl_api.FPLCalls()
    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        exit()
    bootstrap_static = json.loads(bootstrap_static_call.text)

    # print(player_web_name_to_id(bootstrap_static, "Bale"))
    print(get_player_points_per_90_minutes(conn, 543))