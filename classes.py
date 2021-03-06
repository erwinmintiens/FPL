import configparser
import json
import os
from typing import Union
import fpl_api

config = configparser.ConfigParser()
config.read("conf/config.ini")


class Team:
    def __init__(self, team_id: Union[None, int] = None, team_short_name: Union[None, str] = None):
        if not team_id and not team_short_name:
            return
        if team_id:
            self._id = team_id
            self._name = None
            self._short_name = None
            self.set_names()
        else:
            self._short_name = None
            if not os.path.exists(config["settings"]["current_season"] + "/data/teams/all_teams.json"):
                raise FileNotFoundError(f"File {config['settings']['current_season'] + '/data/teams/all_teams.json'} not found")
            with open(config["settings"]["current_season"] + "/data/teams/all_teams.json", "r") as file:
                teams_json = json.load(file)
            for team in teams_json:
                if team_short_name.upper() == team["short_name"]:
                    self._short_name = team["short_name"]
                    self._id = team["id"]
                    self._name = team["name"]
            if not self._short_name:
                raise ValueError(f"Team short name {team_short_name} not found in teams")

    def __str__(self):
        return f'Team {self.name} with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def short_name(self):
        return self._short_name

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @name.setter
    def name(self, new_name):
        self._name = new_name

    @short_name.setter
    def short_name(self, new_short_name):
        self._short_name = new_short_name

    def set_names(self):
        team_json = None
        for file in os.listdir(config["settings"]["current_season"] + "/data/teams/"):
            if file.split("_")[0] == str(self.id):
                with open(config["settings"]["current_season"] + "/data/teams/" + file) as loaded_file:
                    team_json = json.load(loaded_file)
                    self.name = team_json["name"]
                    self.short_name = team_json["short_name"]
        if not team_json:
            self.short_name = None
            self.name = None


class FantasyPremierLeagueManager:
    def __init__(self, person_id: Union[int, str]):
        self._id = int(person_id)
        self._first_name = None
        self._last_name = None
        self._nickname = None
        self.set_names()
        self._info = self.get_info()

    def __str__(self):
        return f'FPL Manager {self.first_name} {self.last_name} (with nickname {self.nickname}) with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def first_name(self):
        return self._first_name

    @property
    def last_name(self):
        return self._last_name

    @property
    def nickname(self):
        return self._nickname

    @property
    def info(self):
        return self._info

    @id.setter
    def id(self, new_id: Union[int, str]):
        self._id = new_id
        self.set_names()

    @first_name.setter
    def first_name(self, new_first_name: str):
        self._first_name = new_first_name

    @last_name.setter
    def last_name(self, new_last_name: str):
        self._last_name = new_last_name

    @nickname.setter
    def nickname(self, new_nickname: str):
        self._nickname = new_nickname

    @info.setter
    def info(self, new_info):
        self._info = new_info

    def get_info(self):
        person_info_call = fpl_api.FPLCalls().get_person_info(self.id)
        if person_info_call.status_code != 200:
            return
        return json.loads(person_info_call.text)

    def set_names(self):
        info = self.get_info()
        if info:
            self._first_name = info["player_first_name"]
            self._last_name = info["player_last_name"]
        else:
            self.first_name = None
            self.last_name = None
        nickname_set = False
        for key, value in config["managers"].items():
            if value == str(self.id):
                self._nickname = key
                nickname_set = True
        if not nickname_set:
            self.nickname = None

    def get_history(self):
        history_call = fpl_api.FPLCalls().get_person_history(self.id)
        if history_call.status_code != 200:
            return
        return json.loads(history_call.text)

    def get_picks_for_gw(self, gameweek: Union[int, str]):
        supported_types = [int, str]
        if type(gameweek) not in supported_types:
            raise TypeError(f"Given variable 'gameweek' is type {type(gameweek)}. Please give type {supported_types}")
        if os.path.exists(f"{config['settings']['current_season']}/data/managers/{self.nickname}_{self.id}.json"):
            with open(f"{config['settings']['current_season']}/data/managers/{self.nickname}_{self.id}.json", "r") as file:
                manager_season_history_json = json.load(file)
        else:
            raise FileNotFoundError(f"File {config['settings']['current_season']}/data/managers/{self.nickname}_{self.id}.json not found")
        for event in manager_season_history_json:
            if event["entry_history"]["event"] == int(gameweek):
                return event
        raise ValueError(f"Gameweek {gameweek} not found in file")


class PremierLeaguePlayer:
    def __init__(self, player_id: int):
        self._id = player_id
        self._first_name = None
        self._second_name = None
        self._web_name = None
        self.set_names()

    def __str__(self):
        return f'Premier League player {self.web_name} with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def first_name(self):
        return self._first_name

    @property
    def second_name(self):
        return self._second_name

    @property
    def web_name(self):
        return self._web_name

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @first_name.setter
    def first_name(self, new_first_name: str):
        self._first_name = new_first_name

    @second_name.setter
    def second_name(self, new_second_name: str):
        self._second_name = new_second_name

    @web_name.setter
    def web_name(self, new_web_name: str):
        self._web_name = new_web_name

    def set_names(self):
        if not os.path.exists(f"{config['settings']['current_season']}/data/bootstrap_static.json"):
            raise FileNotFoundError(f"File {config['settings']['current_season']}/data/bootstrap_static.json not found")
        with open(f"{config['settings']['current_season']}/data/bootstrap_static.json", "r") as file:
            bootstrap_static = json.load(file)

        player_found = False
        for player in bootstrap_static["elements"]:
            if player["id"] == self.id:
                player_found = True
                self.first_name = player["first_name"]
                self.second_name = player["second_name"]
                self.web_name = player["web_name"]
        if not player_found:
            self.first_name = None
            self.second_name = None
            self.web_name = None

    def get_summary(self):
        if not self.web_name:
            raise ValueError(f"Player with ID {self.id} does not have a valid web name")
        # raise None
        if not os.path.exists(f"{config['settings']['current_season']}/data/players/{self.id}_{self.web_name}.json"):
            raise FileNotFoundError(f"File {config['settings']['current_season']}/data/players/{self.id}_{self.web_name}.json not found")

        with open(f"{config['settings']['current_season']}/data/players/{self.id}_{self.web_name}.json", "r") as file:
            return json.load(file)


class Gameweek:
    def __init__(self, gameweek_id):
        self._id = gameweek_id
        self._players_stats = self.get_players_stats()

    def __str__(self):
        return f'Gameweek {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def players_stats(self):
        return self._players_stats

    @id.setter
    def id(self, new_id):
        self._id = new_id

    @players_stats.setter
    def players_stats(self, new_stats):
        self._players_stats = new_stats

    def get_players_stats(self):
        live_call = fpl_api.FPLCalls().get_live_player_stats(self.id)
        if live_call.status_code != 200:
            return
        return json.loads(live_call.text)


class League:
    def __init__(self, league_id: int, league_type="CLASSIC"):
        self._id = league_id
        league_types = ["CLASSIC", "H2H"]
        if league_type not in league_types:
            raise ValueError("Invalid league type. Expected one of: %s" % league_types)
        self._league_type = league_type
        self._name = None
        self.set_name()
        self._properties = self.get_standings()

    def __str__(self):
        return f'League {self.name} with ID {self.id}'

    @property
    def id(self):
        return self._id

    @property
    def league_type(self):
        return self._league_type

    @property
    def name(self):
        return self._name

    @property
    def properties(self):
        return self._properties

    @id.setter
    def id(self, new_id: int):
        self._id = new_id

    @name.setter
    def name(self, new_name: str):
        self._name = new_name

    @league_type.setter
    def league_type(self, new_league_type: str):
        league_types = ["CLASSIC", "H2H"]
        if new_league_type not in league_types:
            raise ValueError("Invalid league type. Expected one of: %s" % league_types)
        self._league_type = new_league_type

    @properties.setter
    def properties(self, new_properties):
        self._properties = new_properties

    def set_name(self):
        standings = self.get_standings()
        self.name = standings["league"]["name"]

    def get_standings(self):
        if self.league_type == "CLASSIC":
            standings_call = fpl_api.FPLCalls().get_classic_league_standings(self.id, page_new_entries=None, page_standings=None, phase=None)
        elif self.league_type == "H2H":
            standings_call = fpl_api.FPLCalls().get_h2h_league_standings(self.id, page_new_entries=None, page_standings=None, phase=None)
        else:
            raise ValueError("Invalid league type. Expected one of: ['CLASSIC', 'H2H']")
        if standings_call.status_code != 200:
            return
        return json.loads(standings_call.text)


class Fixture:
    def __init__(self, fixture_id: Union[None, int]):
        self._id = fixture_id
        self._home_team = None
        self._away_team = None
        self._away_team_score = None
        self._home_team_score = None
        self._started = None
        self._finished = None
        self._goals_scored = None
        self._assists = None
        self._own_goals = None
        self._penalties_saved = None
        self._penalties_missed = None
        self._yellow_cards = None
        self._red_cards = None
        self._saves = None
        self._bonus = None
        self._bps = None
        self._team_h_difficulty = None
        self._team_a_difficulty = None
        self.set_fixture_properties()

    def __str__(self):
        if self.home_team and self.away_team:
            if self.finished:
                return f'Fixture with ID {self.id}: {self.home_team.short_name}-{self.away_team.short_name}: {self.home_team_score}-{self.away_team_score}'
            return f'Fixture with ID {self.id}: {self.home_team.short_name} - {self.away_team.short_name}: Not finished yet'
        return f'Fixture with ID {self.id}: No teams found'

    @property
    def id(self):
        return self._id

    @property
    def home_team(self):
        return self._home_team

    @property
    def away_team(self):
        return self._away_team

    @property
    def home_team_score(self):
        return self._home_team_score

    @property
    def away_team_score(self):
        return self._away_team_score

    @property
    def started(self):
        return self._started

    @property
    def finished(self):
        return self._finished

    @property
    def goals_scored(self):
        return self._goals_scored

    @property
    def assists(self):
        return self._assists

    @property
    def own_goals(self):
        return self._own_goals

    @property
    def penalties_missed(self):
        return self._penalties_missed

    @property
    def penalties_saved(self):
        return self._penalties_saved

    @property
    def yellow_cards(self):
        return self._yellow_cards

    @property
    def red_cards(self):
        return self._red_cards

    @property
    def saves(self):
        return self._saves

    @property
    def bonus_points(self):
        return self._bonus

    @property
    def bps(self):
        return self._bps

    @property
    def team_h_difficulty(self):
        return self._team_h_difficulty

    @property
    def team_a_difficulty(self):
        return self._team_a_difficulty

    @id.setter
    def id(self, new_id):
        self._id = new_id
        self.set_fixture_properties()

    def get_score(self):
        return self.home_team_score, self.away_team_score

    def get_properties(self):
        fixtures_call = fpl_api.FPLCalls().get_fixtures(event=None, only_future_fixtures=False)
        if fixtures_call.status_code != 200:
            return
        fixtures = json.loads(fixtures_call.text)
        for fixture in fixtures:
            if fixture["id"] == self.id:
                return fixture
        return

    def set_fixture_properties(self):
        fixture = None
        for file in os.listdir(config["settings"]["current_season"] + "/data/fixtures/"):
            if self.id == int(file.split("-")[0]):
                # print(self.id, )
                with open(config["settings"]["current_season"] + "/data/fixtures/" + file, "r") as json_file:
                    fixture = json.load(json_file)
        if fixture:
            self._home_team = Team(fixture["team_h"])
            self._away_team = Team(fixture["team_a"])
            self._home_team_score = fixture["team_h_score"]
            self._away_team_score = fixture["team_a_score"]
            self._started = fixture["started"]
            self._finished = fixture["finished"]
            if fixture["stats"]:
                for item in fixture["stats"]:
                    if item["identifier"] == "goals_scored":
                        self._goals_scored = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "assists":
                        self._assists = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "own_goals":
                        self._own_goals = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "penalties_saved":
                        self._penalties_saved = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "penalties_missed":
                        self._penalties_missed = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "yellow_cards":
                        self._yellow_cards = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "red_cards":
                        self._red_cards = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "saves":
                        self._saves = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "bonus":
                        self._bonus = replace_all_player_ids_with_players_in_stats(item)
                    if item["identifier"] == "bps":
                        self._bps = replace_all_player_ids_with_players_in_stats(item)
            self._team_h_difficulty = fixture["team_h_difficulty"]
            self._team_a_difficulty = fixture["team_a_difficulty"]
        else:
            self._home_team = None
            self._away_team = None
            self._away_team_score = None
            self._home_team_score = None
            self._started = None
            self._finished = None
            self._goals_scored = None
            self._assists = None
            self._own_goals = None
            self._penalties_saved = None
            self._penalties_missed = None
            self._yellow_cards = None
            self._red_cards = None
            self._saves = None
            self._bonus = None
            self._bps = None
            self._team_h_difficulty = None
            self._team_a_difficulty = None


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