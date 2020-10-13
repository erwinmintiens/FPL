import json
import math
import os
import random
import sys
import requests
import pandas as pd
import tkinter as tk
from tkinter.ttk import *
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt
import logging
import time
from threading import *


class GUI:
    def __init__(self, master):
        season = get_current_season()
        if not os.path.isfile('config_' + str(season) + '.json'):
            f = open('config_' + str(season) + '.json', "w")
            config = {
                "number_of_players": 0,
                "current_gw": 0,
                "events_finished_this_gw": 0
            }
            json.dump(config, f)
            f.close()
        self.master = master
        master.title("FPL Stats")
        self.label1 = tk.Label(self.master, text="Get", width=20)
        self.label1.grid(row=0, column=0)

        list = ["total_points", "goals_scored", "assists", "clean_sheets", "goals_conceded", "saves", "red_cards",
                "yellow_cards", "penalties_saved", "penalties_missed", "own_goals", "bonus", "bps"]
        self.options = tk.StringVar(self.master)
        self.options.set(list[0])  # default value
        self.w = OptionMenu(self.master, self.options, *list)
        self.w.grid(row=0, column=1)
        self.my_remove(self.options, self.w)
        self.my_add(self.options, list, self.w)

        self.label2 = tk.Label(self.master, text="from")
        self.label2.grid(row=0, column=2)
        self.label3 = tk.Label(self.master, text="in the last")
        self.label3.grid(row=0, column=5)
        self.label4 = tk.Label(self.master, text="gameweeks")
        self.label4.grid(row=0, column=7)
        self.button1 = tk.Button(self.master, text="Run", command=get_player_stats_from_last_x_gws)
        self.button1.grid(row=2, column=0)
        self.updatebutton = tk.Button(self.master, text="Update", command=update_players_dataframes)
        self.updatebutton.grid(row=2, column=7)

        current_gw = get_current_gw()
        self.my_list = ["ALL"]
        for item in range(1, current_gw + 1):
            self.my_list.append(item)
        self.gws = tk.StringVar(self.master)
        self.gws.set("1")
        self.w2 = OptionMenu(master, self.gws, *self.my_list)
        self.w2.grid(row=0, column=6)
        self.my_remove(self.gws, self.w2)
        self.my_add(self.gws, self.my_list, self.w2)

        self.teams_and_players_dict = self.create_team_player_dict()
        self.teams = tk.StringVar(self.master)
        self.teams.trace('w', self.update_options)
        self.players = tk.StringVar(self.master)
        self.teamsmenu = OptionMenu(master, self.teams, *self.teams_and_players_dict.keys())
        self.playersmenu = OptionMenu(master, self.players, '')
        self.teams.set("Arsenal")
        self.teamsmenu.grid(row=0, column=3)
        self.playersmenu.grid(row=0, column=4)

        self.playertext = tk.StringVar()
        self.playertext.set("")
        self.output = tk.Label(self.master, textvariable=self.playertext)
        self.output.grid(row=1, column=0)

        self.progress = tk.StringVar()
        self.progress.set("")
        self.output2 = tk.Label(self.master, textvariable=self.progress)
        self.output2.grid(row=1, column=7)

        self.text_area = tk.Text(self.master, height=10, background="#000000", fg="#FFFFFF", borderwidth=10)
        self.text_area.grid(row=0, column=8, rowspan=3, sticky="NESW")

        sys.stdout = StdoutRedirector(self.text_area)

    def update_options(self, *args):
        teams = self.teams_and_players_dict[self.teams.get()]
        self.players.set(teams[0])
        try:
            menu = self.playersmenu['menu']
            menu.delete(0, 'end')
            for team in teams:
                menu.add_command(label=team, command=lambda nation=team: self.players.set(nation))
        except:
            pass

    def create_team_player_dict(self):
        teams_dict = dict()
        teams = BootstrapStaticSession().all_info["teams"]
        players = BootstrapStaticSession().all_info["elements"]
        for team in teams:
            teams_dict[team["name"]] = []
            for player in players:
                if player["team"] == team["id"]:
                    teams_dict[team["name"]].append(player["web_name"])
                    teams_dict[team["name"]].sort()
        return teams_dict

    def my_remove(self, stringvar, optionmenu):
        stringvar.set('')  # remove default selection only, not the full list
        optionmenu['menu'].delete(0, 'end')  # remove full list

    def my_add(self, stringvar, list, optionmenu):
        self.my_remove(stringvar, optionmenu)  # remove all options
        for opt in list:
            optionmenu['menu'].add_command(label=opt, command=tk._setit(stringvar, opt))
        stringvar.set(list[0])  # default value set


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')

    def flush(self):
        try:
            self.text_space.update()
        except:
            return

    def clear(self):
        self.text_space.delete('1.0', 'end')

    def get(self):
        return self.text_space.get('1.0', 'end-1c')


class pandasModel(QAbstractTableModel):
    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parent=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None


class BootstrapStaticSession:
    def __init__(self):
        session = requests.session()
        url = "https://fantasy.premierleague.com/api/bootstrap-static/"
        r = session.get(url)
        self.all_info = json.loads(r.content)


class Fixtures:
    def __init__(self):
        session = requests.session()
        url = "https://fantasy.premierleague.com/api/fixtures"
        r = session.get(url)
        self.all_info = json.loads(r.content)


class Gameweek:
    def __init__(self, id):
        self.id = id


class Team:
    def __init__(self, id):
        self.id = id
        team_list = create_team_library()
        for item in team_list:
            if item["id"] == id:
                self.name = item["name"]
                self.team_properties = item


class Player:
    def __init__(self, id):
        self.id = id
        session = requests.session()
        # fixtures, history, history_past
        url = "https://fantasy.premierleague.com/api/element-summary/" + str(self.id) + "/"
        r = session.get(url)
        all_info = json.loads(r.content)
        self.fixtures_df = pd.json_normalize(json.loads(r.content)["fixtures"])
        self.history_df = pd.json_normalize(json.loads(r.content)["history"])
        self.history_past_df = pd.json_normalize(json.loads(r.content)["history_past"])

class Update(Thread):
    def run(self):
        print("Updating...")
        app.playertext.set("Updating...")
        season = get_current_season()
        config = load_config(season)
        if not os.path.exists(season + "/players"):
            os.makedirs(season + "/players")
        session = BootstrapStaticSession().all_info
        current_gw = get_current_gw()

        teams_lib = create_team_library()
        teams = {}
        for item in teams_lib:
            teams[item["id"]] = item["name"]

        fixtures = Fixtures()
        events_finished = 0
        for fixture in fixtures.all_info:
            if fixture["event"] == current_gw and fixture["finished"] is True:
                events_finished += 1

        if config["current_gw"] != current_gw or config["events_finished_this_gw"] != events_finished:
            i = 0
            length = len(session['elements'])
            for player in session["elements"]:
                player_id = player["id"]
                player_df_to_pickle(player_id, season)
                print("Processed " + str(player_id))
                app.playertext.set("Updating... " + teams[player["team"]])
                app.progress.set(str(math.ceil((i/length)*100)) + "%")
                i += 1
            config["number_of_players"] = i
            config["current_gw"] = current_gw
            for event in session["events"]:
                if event["id"] == current_gw:
                    config["gw_is_finished"] = event["finished"]
            config["events_finished_this_gw"] = events_finished
            save_config(config, season)
            app.playertext.set("Updating complete.")
            app.progress.set("")
        else:
            if config["number_of_players"] != len(session["elements"]):
                print("Looking for new elements...")
                for player in session["elements"]:
                    if player["id"] > config["number_of_players"]:
                        player_id = player["id"]
                        if not os.path.isfile(
                                season + "/players/" + str(get_player_info("web_name", player_id)) + '_' + str(
                                        player_id) + ".pkl"):
                            player_df_to_pickle(player_id, season)
                            app.playertext.set("Processed new element: " + str(
                                get_player_info("web_name", player_id)) + '_' + str(
                                player_id) + ".pkl")
                            print("Processed new element: " + str(get_player_info("web_name", player_id)) + '_' + str(
                                player_id) + ".pkl")
                        config["number_of_players"] = player_id
                        save_config(config, season)
                app.playertext.set("Processing done.")
                print("Processing done.")
            else:
                app.playertext.set("Up to date.")
                print("Up to date.")
        return


def save_config(config, season):
    f = open('config_' + str(season) + '.json', 'w')
    json.dump(config, f)
    f.close()


def create_team_library():
    teams_library = []
    session = BootstrapStaticSession()
    teams = session.all_info["teams"]
    for team in teams:
        teams_library.append(team)
    return teams_library


def create_player_library():
    player_library = []
    session = BootstrapStaticSession()
    players = session.all_info["elements"]
    for player in players:
       player_library.append(player)
    return player_library


def get_player_details(id):
    list = {}
    session = BootstrapStaticSession()
    if isinstance(id, str):
        for item in session.all_info["elements"]:
            if id.upper() in item["second_name"].upper() or id.upper() in item["web_name"].upper():
                list[item["web_name"]] = item
    elif isinstance(id, int):
        for item in session.all_info["elements"]:
            if item["id"] == id:
                list[item["web_name"]] = item
    else:
        return "Give an int of string."
    return list


def get_team_details(id):
    session = BootstrapStaticSession()
    if isinstance(id, str):
        for item in session.all_info["teams"]:
            if id.upper() in item["name"].upper() or id.upper() in item["short_name"].upper():
                return item
    elif isinstance(id, int):
        for item in session.all_info["teams"]:
            if item["id"] == id:
                return item
    else:
        return "Give an int of string."


def get_player_ppg(id):
    session = BootstrapStaticSession()
    if isinstance(id, int):
        for item in session.all_info["elements"]:
            if item["id"] == id:
                return item["points_per_game"]
    else:
        return "Give an int of string."
    return list


def get_player_id(name):
    session = BootstrapStaticSession()
    for item in session.all_info["elements"]:
        if name.upper() == item["web_name"].upper() or name.upper() == item["second_name"].upper():
            return item["id"]


def get_player_info(info, id):
    session = BootstrapStaticSession()
    for item in session.all_info["elements"]:
        if item["id"] == id:
            return item[info]


def get_current_gw():
    bootstrap_static = BootstrapStaticSession()
    events = bootstrap_static.all_info["events"]
    for item in events:
        if item["is_current"] is True:
            return item["id"]


def get_current_season():
    session = BootstrapStaticSession().all_info
    events = session["events"]
    for event in events:
        if event["id"] == 38:
            return event["deadline_time"][0:4]


def players_to_pandas():
    bootstrap_static = BootstrapStaticSession()
    df = pd.json_normalize(bootstrap_static.all_info["elements"])
    # df.to_excel("excels.xlsx")
    return df


def get_x_players_with_highest_stats_in_last_x_gws(number_of_players, stat, last_gws):
    season = get_current_season()
    players = os.listdir(season + '/players/')
    df_all = None
    i = 1
    for player in players:
        print("Processing player " + str(i))
        df = pickle_to_player_df(season + '/players/' + player)
        df = df.tail(last_gws)
        df = df.drop(columns=['fixture', 'opponent_team', 'was_home', 'kickoff_time', 'round', 'ict_index', 'transfers_balance', 'selected', 'transfers_in', 'transfers_out', 'influence', 'creativity', 'threat', 'team_h_score', 'team_a_score'])
        df.loc['mean'] = df.mean()
        if df_all is None:
            df_all = df.tail(1)
        else:
            df_all = df_all.append(df.tail(1))
        i += 1

    df_all = replace_player_id_with_name_in_df(df_all)
    df_all = df_all.sort_values(by=stat, ascending=False)

    df_all.to_excel("all_last_" + str(last_gws) + "gws.xlsx")


def get_player_history_dataframe(id):
    return Player(id).history_df


def get_player_stats_from_last_x_gws():
    player_id = get_player_id(app.players.get())
    stats = app.options.get()
    number_of_last_gws = app.gws.get()
    season = get_current_season()

    if number_of_last_gws == "ALL":
        number_of_last_gws = get_current_gw()
    else:
        number_of_last_gws = int(number_of_last_gws)

    df = pickle_to_player_df(
        season + '/players/' + str(get_player_info("web_name", player_id)) + '_' + str(player_id) + ".pkl")
    df = df.tail(number_of_last_gws)
    df.drop(df.columns.difference([stats]), 1, inplace=True)
    sum = df.sum()
    # df.index = df.index + 1
    df.index.name = "GW"

    if stats in df:
        stats_in_last_x_gws = df[stats].sum()
        print(str(get_player_info("web_name", player_id)))
        print(df)
        print("Total", "\t", sum.values[0])
        # df.to_excel("bamford.xlsx")
        # app.playertext.set(str(stats_in_last_x_gws))
        return stats_in_last_x_gws
    else:
        return


def replace_team_id_with_team_name_in_df(df):
    team_library = create_team_library()
    teams = {}
    for item in team_library:
        teams[item["id"]] = item["name"]
    df = df.replace({"opponent_team": teams})
    return df


def replace_player_id_with_name_in_df(df):
    player_library = create_player_library()
    players = {}
    for player in player_library:
        players[player["id"]] = player["web_name"]
    df = df.replace({"element": players})
    return df


def player_df_to_pickle(id, season):
    df = get_player_history_dataframe(id)
    df.index = df.index + 1
    df.to_pickle(season + '/players/' + str(get_player_info("web_name", id)) + '_' + str(id) + ".pkl")


def pickle_to_player_df(filename):
    df = pd.read_pickle(filename)
    return df


def update_players_dataframes():
    update = Update()
    update.start()


def show_data_table(df):
    app2 = QApplication(sys.argv)
    model = pandasModel(df)
    view = QTableView()
    view.setModel(model)
    view.resize(1600, 600)
    view.show()
    sys.exit(app2.exec_())


def load_config(season):
    with open('config_' + str(season) + '.json', 'r') as f:
        config = json.load(f)
    f.close()
    return config


def thread_function(name):
    logging.info("Thread %s: starting", name)
    time.sleep(2)
    logging.info("Thread %s: finishing", name)


if __name__ == '__main__':

    # show_data_table(df)

    # get_x_players_with_highest_stats_in_last_x_gws(None, 'total_points', 2)

    root = tk.Tk()
    root.configure(border=3)
    app = GUI(root)
    root.mainloop()
