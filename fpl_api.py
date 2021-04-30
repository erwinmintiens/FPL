import requests


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
    def get_bootstrap_static(self):
        url = f"{self._base_url}/bootstrap-static/"
        if not self._base_url:
            return
        return requests.get(url=url)

    def get_person_picks(self, person_id=None, gameweek=None):
        if not self._base_url or not person_id or not gameweek:
            return
        url = f"{self._base_url}/entry/{person_id}/event/{gameweek}/picks/"
        return requests.get(url=url)

    def get_player_summary(self, player_id=None):
        if not player_id:
            return
        url = f"{self._base_url}/element-summary/{player_id}/"
        return requests.get(url=url)

    def get_event_status(self, gameweek=None):
        if not gameweek:
            return
        url = f"{self._base_url}/event-status"
        return requests.get(url=url)

    def get_fixtures(self):
        url = f"{self._base_url}/fixtures"
        return requests.get(url=url)

    def get_live_player_stats(self, gameweek):
        if not gameweek:
            return
        url = f"{self._base_url}/event/{gameweek}/live/"
        return requests.get(url=url)

    def get_league_details(self, league_id):
        if not league_id:
            return
        url = f"{self._base_url}/leagues-classic/{league_id}"
        return requests.get(url=url)
