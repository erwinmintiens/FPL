from typing import Union
import fpl_api
import json
import configparser
import __init__

__init__.setup()

config = configparser.ConfigParser()
config.read("conf/config.ini")


class Team:
    def __init__(self, team_id):
        self._id = team_id
        self._name = None
        self._short_name = None
        self.set_names()

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
        self.set_names()

    def get_info(self):
        bootstrap_static_call = fpl_api.FPLCalls().get_bootstrap_static()
        if bootstrap_static_call.status_code != 200:
            return
        bootstrap_static = json.loads(bootstrap_static_call.text)
        for team in bootstrap_static["teams"]:
            if team["id"] == self.id:
                return team

    def set_names(self):
        team = self.get_info()
        self._name = team["name"]
        self._short_name = team["short_name"]


class FantasyPremierLeagueManager:
    def __init__(self, person_id: int):
        self._id = person_id
        self._first_name = None
        self._last_name = None
        self._history = self.get_history()
        self._info = self.get_info()

    def __str__(self):
        return f'FPL Manager {self.first_name} {self.last_name} with ID {self.id}'

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
    def history(self):
        return self._history

    @property
    def info(self):
        return self._info

    @id.setter
    def id(self, new_id):
        self._id = new_id
        self.set_names()

    @history.setter
    def history(self, new_history):
        self._history = new_history

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
        self._first_name = info["player_first_name"]
        self._last_name = info["player_last_name"]

    def get_history(self):
        history_call = fpl_api.FPLCalls().get_person_history(self.id)
        if history_call.status_code != 200:
            return
        return json.loads(history_call.text)

    def get_picks_for_gw(self, gameweek: Union[int, str]):
        picks_call = fpl_api.FPLCalls().get_person_picks(self.id, gameweek)
        if picks_call.status_code != 200:
            return
        return json.loads(picks_call.text)


class PremierLeaguePlayer:
    def __init__(self, player_id: int):
        self._id = player_id
        self._first_name = None
        self._second_name = None
        self._web_name = None
        self.set_names()
        self._stats = self.get_summary()

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

    @property
    def stats(self):
        return self._stats

    @id.setter
    def id(self, new_id):
        self._id = new_id

    def set_names(self):
        bootstrap_static_call = fpl_api.FPLCalls().get_bootstrap_static()
        if bootstrap_static_call.status_code != 200:
            return
        for player in json.loads(bootstrap_static_call.text)["elements"]:
            if player["id"] == self.id:
                self._first_name = player["first_name"]
                self._second_name = player["second_name"]
                self._web_name = player["web_name"]

    def get_summary(self):
        summary_call = fpl_api.FPLCalls().get_player_summary(self.id)
        if summary_call.status_code != 200:
            return
        return json.loads(summary_call.text)


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


def player_id_to_name(bootstrap_static_json, player: PremierLeaguePlayer):
    for item in bootstrap_static_json["elements"]:
        if item["id"] == player.id:
            return item["web_name"]
    return None


def player_web_name_to_id(bootstrap_static_json, web_name: str):
    for item in bootstrap_static_json["elements"]:
        if item["web_name"] == web_name:
            return item["id"]
    return None


def get_person_captain_for_gameweek(fpl_connection: fpl_api.FPLCalls, manager: FantasyPremierLeagueManager, gameweek: Union[int, str]):
    captain_played = False
    vice_captain_played = False
    is_triple_captain = False
    person_picks_call = fpl_connection.get_person_picks(manager.id, gameweek)
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


def get_points_for_player(player: PremierLeaguePlayer, gameweek: Union[int, str]):
    player_summary = player.get_summary()
    total = 0
    for gw in player_summary["history"]:
        if gw["round"] == gameweek:
            total += gw["total_points"]
    return total


def get_extra_captaincy_points_between_gws(fpl_connection: fpl_api.FPLCalls, manager: FantasyPremierLeagueManager, lower_gw: Union[int, str], upper_gw: Union[int, str]):
    result = list()
    for gameweek in range(lower_gw, upper_gw + 1):
        captain = get_person_captain_for_gameweek(fpl_connection, manager, gameweek)
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


def get_player_points_per_minute(player: PremierLeaguePlayer):
    player_info = player.get_summary()
    minutes = 0
    points = 0
    for game in player_info["history"]:
        minutes += game["minutes"]
        points += game["total_points"]
    return points/minutes


def get_player_points_per_90_minutes(player: PremierLeaguePlayer):
    ppm = get_player_points_per_minute(player)
    if ppm is None:
        return
    return ppm * 90


if __name__ == '__main__':
    erwin = FantasyPremierLeagueManager(config["managers"]["erwin"])
    bale = PremierLeaguePlayer(543)
    arsenal = Team(1)
    schuppebekske = League(435851)

    print(bale.stats)