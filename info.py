import os
from typing import Union
import fpl_api
import json
import configparser
import __init__
import data
from classes import PremierLeaguePlayer, FantasyPremierLeagueManager, League, Fixture, Team

config = configparser.ConfigParser()
config.read("conf/config.ini")

player_stats = ["total_points", "minutes", "goals_scored", "assists", "clean_sheets", "goals_conceded", "own_goals",
             "penalties_saved", "penalties_missed", "yellow_cards", "red_cards", "saves", "bonus", "bps", "influence",
             "creativity", "threat", "ict_index", "value", "transfers_balance", "selected", "transfers_in",
             "transfers_out"]

fixture_stats = ["goals_scored", "assists", "own_goals", "penalties_saved", "penalties_missed", "yellow_cards",
                 "red_cards", "saves", "bonus", "bps"]


def replace_player_id_with_player_object(text):
    if text:
        if type(text) == dict:
            if "element" in text:
                text["element"] = PremierLeaguePlayer(text["element"])
        elif type(text) == list:
            for dictionary in text:
                if "element" in dictionary:
                    dictionary["element"] = PremierLeaguePlayer(dictionary["element"])
        else:
            raise TypeError(f"Parameter with type {type(text)} is not supported for this function")
    return text


def replace_all_player_ids_with_players_in_stats(stat: dict):
    if not stat["a"] and not stat["h"]:
        return
    for element in stat["a"]:
        if "element" in element:
            element["element"] = PremierLeaguePlayer(element["element"])
    for element in stat["h"]:
        if "element" in element:
            element["element"] = PremierLeaguePlayer(element["element"])
    return stat



def get_all_teams():
    bootstrap_static_call = fpl_api.FPLCalls().get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)
    teams = list()
    for team in bootstrap_static["teams"]:
        teams.append(team["name"].lower())
        teams.append(team["short_name"].lower())
    return teams


def get_all_team_ids():
    bootstrap_static_call = fpl_api.FPLCalls().get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)
    teams = list()
    for team in bootstrap_static["teams"]:
        teams.append(team["id"])
    return teams


def team_name_to_id(team_name: str):
    teams = get_all_teams()
    if team_name.lower() not in teams:
        raise ValueError(f"Team {team_name.lower()} not found.")
    bootstrap_static_call = fpl_api.FPLCalls().get_bootstrap_static()
    if bootstrap_static_call.status_code != 200:
        return
    bootstrap_static = json.loads(bootstrap_static_call.text)
    for team in bootstrap_static["teams"]:
        if team_name.lower() in [team["name"].lower(), team["short_name"].lower()]:
            return team["id"]


def player_web_name_to_id(bootstrap_static_json, web_name: str) -> Union[None, int]:
    for item in bootstrap_static_json["elements"]:
        if item["web_name"] == web_name:
            return item["id"]
    return None


def get_person_captain_for_gameweek(manager: FantasyPremierLeagueManager, gameweek: Union[int, str]) -> Union[None, list]:
    captain_played = False
    vice_captain_played = False
    is_triple_captain = False
    person_picks = manager.get_picks_for_gw(gameweek)
    if not person_picks:
        return
    for player in person_picks["picks"]:
        if player["is_captain"] and player["multiplier"] not in [0, 1]:
            if player["multiplier"] == 3:
                is_triple_captain = True
            captain_played = True
            return [PremierLeaguePlayer(player["element"]), captain_played, vice_captain_played, is_triple_captain]
        if player["is_vice_captain"] and player["multiplier"] not in [0, 1]:
            if player["multiplier"] == 3:
                is_triple_captain = True
            vice_captain_played = True
            return [PremierLeaguePlayer(player["element"]), captain_played, vice_captain_played, is_triple_captain]
    return [None, captain_played, vice_captain_played, is_triple_captain]


def get_points_for_player(player: PremierLeaguePlayer, gameweek: Union[int, str]) -> Union[None, int]:
    player_summary = player.get_summary()
    if not player_summary:
        return
    total = 0
    for gw in player_summary:
        if gw["round"] == gameweek:
            total += gw["total_points"]
    return total


def get_extra_captaincy_points_between_gws(manager: FantasyPremierLeagueManager, lower_gw: Union[int, str], upper_gw: Union[int, str]) -> Union[None, list]:
    result = list()
    for gameweek in range(lower_gw, upper_gw + 1):
        captain = get_person_captain_for_gameweek(manager, gameweek)
        if type(captain) is list:
            if captain[0] is not None:
                if captain[3]:
                    result.append(get_points_for_player(captain[0], gameweek) * 2)
                else:
                    result.append(get_points_for_player(captain[0], gameweek))
            else:
                result.append(0)
        else:
            return
    return result


def get_player_stats_in_gw(player: PremierLeaguePlayer, gameweek: Union[int, str]) -> Union[None, list]:
    if not player.stats:
        player.stats = player.get_summary()
    if not player.stats:
        return
    stats = list()
    for element in player.stats["history"]:
        if element["round"] == int(gameweek):
            stats.append(element)
    return stats


def get_player_stat_per_90_minutes(player: PremierLeaguePlayer, stat: str) -> Union[None, float]:
    global player_stats
    if stat not in player_stats:
        raise ValueError(f"Stat {stat} not one of {player_stats}")
    if not player.stats:
        player.stats = player.get_summary()
    if not player.stats:
        return
    stat_total = 0
    minutes = 0
    if stat in ["influence", "creativity", "threat", "ict_index"]:
        for game in player.stats["history"]:
            stat_total += float(game[stat])
            minutes += game["minutes"]
    else:
        for game in player.stats["history"]:
            stat_total += game[stat]
            minutes += game["minutes"]
    return stat_total / minutes * 90


def get_player_stat_per_game(player: PremierLeaguePlayer, stat: str) -> Union[None, float]:
    global player_stats
    if stat not in player_stats:
        raise ValueError(f"Stat {stat} not one of {player_stats}")
    if not player.stats:
        player.stats = player.get_summary()
    if not player.stats:
        return
    stat_total = 0
    games = 0
    if stat in ["influence", "creativity", "threat", "ict_index"]:
        for game in player.stats["history"]:
            if game["minutes"] > 0:
                stat_total += float(game[stat])
                games += 1
    else:
        for game in player.stats["history"]:
            if game["minutes"] > 0:
                stat_total += game[stat]
                games += 1
    return stat_total / games


def get_fixture(home_team: Team, away_team: Team) -> Union[None, Fixture]:
    fixtures_call = fpl_api.FPLCalls().get_fixtures(event=None, only_future_fixtures=False)
    if fixtures_call.status_code != 200:
        return
    fixtures = json.loads(fixtures_call.text)
    for fixture in fixtures:
        if fixture["team_h"] == home_team.id and fixture["team_a"] == away_team.id:
            return Fixture(fixture["id"])
    return


def get_captaincy_points_per_manager(lower_gameweek: int, upper_gameweek: int) -> dict:
    points = dict()
    for manager in config["managers"]:
        points[manager] = get_extra_captaincy_points_between_gws(FantasyPremierLeagueManager(config["managers"][manager]), lower_gameweek, upper_gameweek)
    if points == dict():
        raise KeyError("No managers found in config.ini")
    return points


def update_all_files():
    data.fetch_all_latest_info()


if __name__ == '__main__':
    update_all_files()
    erwin = FantasyPremierLeagueManager(config["managers"]["erwin"])
    bale = PremierLeaguePlayer(543)
    team1 = Team(14)
    team2 = Team(20)
    schuppebekske = League(435851)
    een_fixture = Fixture(200)
    manchester_united = Team(team_short_name="MUN")
    mun_mci = get_fixture(manchester_united, Team(team_short_name="MCI"))

    # print(mun_mci.away_team)
    print(een_fixture.yellow_cards)
    print(get_captaincy_points_per_manager(34, 35))

