import requests
from bs4 import BeautifulSoup
from table import StatTable
from constants import *
from flask_restful import Resource
import collections

class Espn_api(Resource):
    global url_prefix
    url_prefix = "https://www.espn.com/nfl/boxscore/_/gameId/"

    @classmethod
    def get(cls):
        return cls.convert_to_json(cls.get_team_stats(401326595)), 200

    @classmethod
    def convert_to_json(cls, data):
        json = collections.defaultdict(dict)
        json['table_names'] = [table.type for table_id, table in data.items()]
        json['columns'] = [table.attributes for table_id, table in data.items()]
        for table_id, table in data.items():
            json['tables'][table.type + "-Home"] = table.home_rows
            json['tables'][table.type + "-Away"] = table.away_rows
        return json

    @classmethod
    def get_team_stats(cls, game_id):
        team_stats_response = requests.get(url_prefix + str(game_id))
        team_stats_soup = BeautifulSoup(team_stats_response.text, 'html.parser')
        return cls.get_data(team_stats_soup)

    @classmethod
    def get_data(cls, soup):
        cls.get_data_by_id(soup, "gamepackage-rushing")
        return {table_id : cls.get_data_by_id(soup, table_id) for table_id in TABLE_IDS}

    @classmethod
    def get_data_by_id(cls, soup, table_id):
        data = soup.find("div", {"id":table_id})
        away_table_rows, home_table_rows = cls.get_table_rows(data)
        table = StatTable().createTable(table_id)
        cls.populate_table_rows(table, away_table_rows, home_table_rows)
        return table

    @classmethod
    def get_table_rows(cls, data):
        away_data = data.find("div", class_="gamepackage-away-wrap")
        away_table = away_data.find("table", class_="mod-data").find("tbody")
        away_table_rows = set(away_table.find_all("tr")).difference(away_table.find_all("tr", class_="highlight"))

        home_data = data.find("div", class_="gamepackage-home-wrap")
        home_table = home_data.find("table", class_="mod-data").find("tbody")
        home_table_rows = set(home_table.find_all("tr")).difference(home_table.find_all("tr", class_="highlight"))

        return away_table_rows, home_table_rows

    @classmethod
    def populate_table_rows(cls, table, away_rows, home_rows):
        try:
            for row in away_rows:
                name_data = row.find("td", class_="name")
                name = next(iter(set(name_data.find_all("span")).difference(name_data.find_all("span", class_="abbr")))).text
                table.add_away_row([name] + [row.find("td", class_=attr).text for attr in table.attributes])
        except Exception:
            table.add_empty_away_row()
        try:
            for row in home_rows:
                name_data = row.find("td", class_="name")
                name = next(iter(set(name_data.find_all("span")).difference(name_data.find_all("span", class_="abbr")))).text
                table.add_home_row([name] + [row.find("td", class_=attr).text for attr in table.attributes])
        except Exception:
            table.add_empty_home_row()
