import json
import fpl_api


def player_id_to_name(bootstrap_static_json, player_id):
    for item in bootstrap_static_json["elements"]:
        if item["id"] == player_id:
            return item["web_name"]
    return None


def player_web_name_to_id(bootstrap_static_json, web_name):
    for item in bootstrap_static_json["elements"]:
        if item["web_name"] == web_name:
            return item["id"]
    return None


def get_person_captain_for_gameweek(fpl_connection: fpl_api.FPLCalls, person_id, gameweek):
    person_picks_call = fpl_connection.get_person_picks(person_id, gameweek)
    if person_picks_call.status_code != 200:
        return
    person_picks = json.loads(person_picks_call.text)
    for player in person_picks["picks"]:
        if player["is_captain"]:
            return player["element"]
    return


if __name__ == '__main__':
    # person_ids = [435872, 412783, 1986671, 4410825, 3992968, 4440492, 3725741, 3126551, 4578815]
    persons = [
        {
            "name": "arthur",
            "id": 435872
        },
        {
            "name": "louis",
            "id": 412783
        },
        {
            "name": "erwin",
            "id": 1986671
        },
        {
            "name": "pieter",
            "id": 4410825
        },
        {
            "name": "gert",
            "id": 3992968
        },
        {
            "name": "michiel",
            "id": 4440492
        },
        {
            "name": "wouter",
            "id": 3126551
        },
        {
            "name": "stijn",
            "id": 3725741
        },
        {
            "name": "niels",
            "id": 4578815
        }
    ]

    conn = fpl_api.FPLCalls()

    bootstrap_static_call = conn.get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        exit()
    bootstrap_static = json.loads(bootstrap_static_call.text)

    for gameweek in range(25,34):
        print(f"GW {gameweek}")
        for person in persons:
            print(person["name"] + ": " + player_id_to_name(bootstrap_static, get_person_captain_for_gameweek(conn, person["id"], gameweek)))
        print("################################################")
