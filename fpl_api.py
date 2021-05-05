import requests
from typing import Union


class FPLCalls:
    def __init__(self, base_url="https://fantasy.premierleague.com/api"):
        self._base_url = base_url

    @property
    def base_url(self):
        return self._base_url

    @base_url.setter
    def base_url(self, new_base_url):
        self._base_url = new_base_url

    # API CALLS
    def get_bootstrap_static(self) -> requests.Response:
        """ Get general Fantasy Premier League info about the season

        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The gameweeks within the current season;
                    The overall settings of Fantasy Premier League;
                    The phases of the current season;
                    Properties of the Premier League teams within the current season;
                    The total Fantasy Premier League players;
                    Premier League player properties;
                    Properties of the types of Premier League Players.
            This call returns and empty requests.Response with a 404 status code if self.base_url is None.
        """
        if not self.base_url:
            response = requests.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/bootstrap-static/"
        return requests.get(url=url)

    def get_person_picks(self, person_id: Union[int, str], gameweek: Union[int, str]) -> requests.Response:
        """ Get picks for a specific Fantasy Premier League manager in a specific gameweek.

        :param person_id: (int) or (str) | ID of the person.
        :param gameweek: (int) or (str) | gameweek. Values 1 to 38.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    Active chip within that gameweek;
                    Automatic substitutions within that gameweek;
                    Properties of the Fantasy Premier League team within that gameweek;
                    The chosen lineup of the Fantasy Premier League manager within that gameweek.
            This call returns and empty requests.Response with a 404 status code if self.base_url, person_id or gameweek is None.
        """
        if not self.base_url or not person_id or not gameweek:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/entry/{person_id}/event/{gameweek}/picks/"
        return requests.get(url=url)

    def get_player_summary(self, player_id: Union[int, str]) -> requests.Response:
        """ Get summary for a specific Premier League player.

        :param player_id: (int) or (str) | ID of the premier league player.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    Fixtures of the Premier League player;
                    History of the Premier League player within the current season;
                    History of the Premier League player from the past seasons in the Premier League.
            This call returns and empty requests.Response with a 404 status code if self.base_url or player_id is None.
        """
        if not self.base_url or not player_id:
            response = requests.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/element-summary/{player_id}/"
        return requests.get(url=url)

    def get_event_status(self) -> requests.Response:
        """ Get status of the last or ongoing gameweek.

        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    Status about the current/last gameweek.
            This call returns and empty requests.Response with a 404 status code if self.base_url is None.
        """
        if not self.base_url:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/event-status"
        return requests.get(url=url)

    def get_fixtures(self, event: Union[None, int], only_future_fixtures: bool) -> requests.Response:
        """ Get fixtures for games in the season.

        :param event:
            (None) or (int) | gameweek from which the fixtures will be fetched.
            If set to None, all fixtures within the season will be fetched.
        :param only_future_fixtures:
            (bool) | If set to True, only future fixtures will be fetched.
            This parameter only works if parameter event is set to False.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    Properties of Premier League fixtures within the current season.
            This call returns and empty requests.Response with a 404 status code if self.base_url is None.
        """
        if not self.base_url:
            response = requests.models.Response()
            response.status_code = 404
            return response
        params = {}
        if event:
            if event not in range(1, 39):
                raise ValueError(f"Event {event} is not a value from 1 to 38")
            params["event"] = event
        if only_future_fixtures:
            params = {"future": 1}
        url = f"{self.base_url}/fixtures"
        return requests.get(url=url, params=params)

    def get_live_player_stats(self, gameweek: Union[int, str]) -> requests.Response:
        """ Get all Premier League player performances within a specific gameweek.

        :param gameweek: (int) or (str) | gameweek. Values 1 to 38.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    Properties of each Premier League player that played/plays within this gameweek.
            This call returns and empty requests.Response with a 404 status code if self.base_url or gameweek is None.
        """
        if not self.base_url or not gameweek:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/event/{gameweek}/live/"
        return requests.get(url=url)

    def get_classic_league_details(self, league_id: Union[int, str]) -> requests.Response:
        """ Get classic league information bases on a league ID.

        :param league_id: (int) or (str) | ID of the league.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The classic league properties.
            This call returns and empty requests.Response with a 404 status code if self.base_url or gameweek is None.
        """
        if not self.base_url or not league_id:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/leagues-classic/{league_id}/"
        return requests.get(url=url)

    def get_classic_league_standings(self, league_id: Union[int, str], page_new_entries: Union[int, str, None], page_standings: Union[int, str, None], phase: Union[int, str, None]) -> requests.Response:
        """ Get standings of a specific classic league.

        :param league_id: (int) or (str) | ID of the classic league.
        :param page_new_entries: (int), (str) or None | Page displayed of new entries in the classic league. Default value = 1.
        :param page_standings: (int), (str) or None | Page displayed of the standings within the classic league. Default value = 1.
        :param phase: (int), (str) or None | Phases of the season as described in the bootstrap static call. Default value = 1 (overall).
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The classic league properties;
                    The classic league new entries;
                    The classic league standings.
            This call returns and empty requests.Response with a 404 status code if self.base_url or league_id is None.
        """
        if not self.base_url or not league_id:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/leagues-classic/{league_id}/standings/"
        params = dict()
        if page_new_entries:
            params["page_new_entries"] = page_new_entries
        if page_standings:
            params["page_standings"] = page_standings
        if phase:
            params["page_standings"] = page_standings
        return requests.get(url=url, params=params)

    def get_h2h_league_standings(self, league_id: Union[int, str], page_new_entries: Union[int, str, None], page_standings: Union[int, str, None], phase: Union[int, str, None]) -> requests.Response:
        """ Get standings of a specific Head To Head (H2H) league.

        :param league_id: league_id: (int) or (str) | ID of the H2H league.
        :param page_new_entries: (int), (str) or None | Page displayed of new entries in the H2H league. Default value = 1.
        :param page_standings: (int), (str) or None | Page displayed of the standings within the H2H league. Default value = 1.
        :param phase: (int), (str) or None | Phases of the season as described in the bootstrap static call. Default value = 1 (overall).
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The H2H league properties;
                    The H2H league new entries;
                    The H2H league standings.
            This call returns and empty requests.Response with a 404 status code if self.base_url or league_id is None.
        """
        if not self.base_url or not league_id:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/leagues-h2h/{league_id}/standings/"
        params = dict()
        if page_new_entries:
            params["page_new_entries"] = page_new_entries
        if page_standings:
            params["page_standings"] = page_standings
        if phase:
            params["page_standings"] = page_standings
        return requests.get(url=url, params=params)

    def get_person_info(self, person_id: Union[int, str]) -> requests.Response:
        """ Get info about a Fantasy Premier League manager.

        :param person_id: (int) or (str) | ID of the Fantasy Premier League manager.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The Fantasy Premier League manager properties;
                    The Fantasy Premier League manager team properties;
                    The joined classic leagues;
                    The joined h2h leagues;
                    Cup matches.
            This call returns and empty requests.Response with a 404 status code if self.base_url or league_id is None.
        """
        if not self.base_url or not person_id:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/entry/{person_id}/"
        return requests.get(url=url)

    def get_person_history(self, person_id: Union[int, str]) -> requests.Response:
        """ Get history about a Fantasy Premier League manager.

        :param person_id: (int) or (str) | ID of the Fantasy Premier League manager.
        :return:
            (requests.Response) | requests.Response.text contains JSON info if the call was successful. The object has a 200 status code if the call succeeds.
                This JSON contains info about:
                    The Fantasy Premier League manager team statistics per gameweek throughout the current season;
                    Total points and ranking in previous seasons;
                    When a manager played which chips in the current season.
            This call returns and empty requests.Response with a 404 status code if self.base_url or league_id is None.
        """
        if not self.base_url or not person_id:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/entry/{person_id}/history/"
        return requests.get(url=url)

    def get_dream_team(self, gameweek: Union[int, str]) -> requests.Response:
        if not self.base_url or not gameweek:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/dream-team/{gameweek}/"
        return requests.get(url=url)

    def get_most_valuable_teams(self) -> requests.Response:
        if not self.base_url:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/stats/most-valuable-teams/"
        return requests.get(url=url)

    def get_best_classic_private_leagues(self) -> requests.Response:
        if not self.base_url:
            response = requests.models.Response()
            response.status_code = 404
            return response
        url = f"{self.base_url}/stats/best-classic-private-leagues/"
        return requests.get(url=url)
