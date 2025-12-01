import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.tournamentsoftware.com/",
    "Connection": "keep-alive",
}

#TODO currently using cookies from browser session, need a fix for this
COOKEIS = {
    "ASP.NET_SessionId": "mf0eemxpvsng500mplkaq3df",
    "euconsent-v2": "CQZ8xwAQZ8xwADsACAENCCFkAP_gAEPgAAhoLstR_G__bWlr-bb3aftkeYxP9_hr7sQxBgbJk24FzLvW7JwXx2E5NAzatqIKmRIAu3TBIQNlHJDURVCgKIgVryDMaEyUoTNKJ6BkiFMRI2NYCFxvm4tjWQCY5vr99lc1mB-N7dr82dzyy6hHn3a5_2S1WJCdIYetDfv8ZBKT-9IEd_x8v4v4_F7pE2-eS1n_pGvp6j9-YnM_dBmxt-bSffzPn__rl_e7X_vd_n37v94XH77v____f_-7___2C7AAJhoVEEZYECAQKBhBAgAUFYQAUCAIAAEgYICAEwYFOQMAF1hMgBACgAGCAEAAIMAAQAAAQAIRABQAQCAACAQKAAMACAICAAgYAAQAWIgEAAIDoGKYEEAgWACRmVQaYEoACQQEtlQgkAwIK4QhFngEECImCgAAAAAKAAAAeCwEJJASoSCALiCaAAAgAAAiBAgQSEmAAKgzRaA8CTqMjTAMHzBIgp0GQBMEZCQaEJvQkHikKIUEGQGhSzAHAAAA.YAAAAAAAAAAA",
    "lvt": "K7yBTRpeL0yYWHKfaj0jjsuUw6KXjNsWYtZqI4DZ/8voA7TbsAjx2BP5W2AGt/T45q5DW6qWMYaYQR+gSr/a7Z5zwFExQOzILqyzlV+tfr522l5OIxKuJrYdsnsNeV93r37lkDjFHHqi6NsVT/HfK0nJcADyZGmA86g7ysK7WiwwUfU3fuaMQoCvoNAYV+C4",
    "st": "l=1033&exp=46349.8850925347&c=1&cp=23&s=2"
}

URL_PART_MATCHES = "/matches"

class WebScraper():
    def __init__(self, url, output, verbose=False):
        self.verbose = verbose
        self.output = output #TODO build out information printing logic
        self.url = url

        self.tournament_title = ""
        self.tournament_start = ""
        self.tournament_end = ""
        self.matches_list = []
        self.rawMatchesObjects_list = []
        self.tounament_days_list = []

        self.__runScraper()



    def __runScraper(self):
        self.__getTournamentMetadata()
        self.__getGamesResults()


    def __getTournamentMetadata(self):
        response = requests.get(self.url, headers = HEADERS, cookies = COOKEIS)
        if response.status_code != 200:
            raise Exception(f"bad response code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        self.tournament_title = soup.find("h2", class_=["media__title", "media__title--large"]).get_text(strip=True)

        timeline_metadata = soup.find("div", class_=["tournament-meta__timeline"])
        start_element = timeline_metadata.find("li", class_=["is-started"])
        end_element = timeline_metadata.find("li", class_=["is-finished"])

        self.tournament_start = start_element.find("time").get("datetime").split("T")[0]
        self.tournament_end = end_element.find("time").get("datetime").split("T")[0]
        if self.tournament_start != self.tournament_end:
            #TODO need to add all days in between start end and to support tournaments that last more than 2 days, but not currently relevant for me
            self.tounament_days_list = [self.tournament_start.replace("-",""), self.tournament_end.replace("-","")]
        else:
            self.tounament_days_list = [self.tournament_start.replace("-","")]


    def __getGamesResults(self):
        for tournament_day in self.tounament_days_list:
            url = self.url + URL_PART_MATCHES + "/" + tournament_day
            response = requests.get(url, headers = HEADERS, cookies = COOKEIS)
            if response.status_code != 200:
                raise Exception(f"bad response code: {response.status_code}")

            soup = BeautifulSoup(response.text, "html.parser")
            #self.tournament_title = soup.find("title").get_text()

            raw_matches = soup.find_all("div",class_=["match","match--list"])
            for raw_match in raw_matches:
                match_dict = {}
                team_one_scores = []
                team_two_scores = []

                match_header = raw_match.find("li", class_=["match__header-title-item"]).get_text(strip=True)
                players_result = raw_match.find_all("div", class_=["match__row"])
                match_results = raw_match.find_all("li", class_=["points__cell"])


                team_one = players_result[0].find("div", class_=["match__row-title"]).get_text("+", strip=True)
                team_two = players_result[1].find("div", class_=["match__row-title"]).get_text("+", strip=True)
                team_one_status = players_result[0].find("span", class_=["tag"])
                team_two_status = players_result[1].find("span", class_=["tag"])

                # if status item exists we want it's text value
                if team_one_status != None:
                    team_one_status = team_one_status.get_text(strip=True)
                if team_two_status != None:
                    team_two_status = team_two_status.get_text(strip=True)

                #TODO this is initial hack to have scores for walkovers, final solutions should handle no score situations
                if len(match_results) == 0:
                    if team_one_status == 'W':
                        team_one_scores.append(1)
                        team_two_scores.append(0)
                    else:
                        team_one_scores.append(0)
                        team_two_scores.append(1)

                #removing placement data from name
                team_one = re.sub(" .\d.","", team_one)
                team_two = re.sub(" .\d.","", team_two)

                for i in range(len(match_results)):
                    if i % 2 == 0:
                        team_one_scores.append(match_results[i].get_text(" ", strip=True))
                    else:
                        team_two_scores.append(match_results[i].get_text(" ", strip=True))
                match_dict[team_one] = team_one_scores
                match_dict[team_two] = team_two_scores

                category = match_header.split(" ", 1)[0]
                league = match_header.split(" ", 1)[1].split("-")[0].strip()

                # print("--- DATA ---")
                # print("header:", match_header)
                # print("category:", category)
                # print("league:", league)
                # print(f"Team: '{team_one}' with result: '{team_one_status}' and game scores '{team_one_scores}'")
                # print(f"Team: '{team_two}' with result: '{team_two_status}' and game scores '{team_two_scores}'")
                # print("Final dictionary of the match:")
                # print(match_dict)
                # print("")

                new_raw_match = RawMatch(category, league, team_one, team_one_status, team_one_scores, team_two, team_two_status, team_two_scores)

                self.matches_list.append(match_dict)
                self.rawMatchesObjects_list.append(new_raw_match)


class RawMatch():
    def __init__(self, category, league, team_one, team_one_status, team_one_scores, team_two, team_two_status, team_two_scores):
        self.category = category
        self.league = league
        self.team_one = team_one
        self.team_one_status = team_one_status
        self.team_one_scores = team_one_scores
        self.team_two = team_two
        self.team_two_status = team_two_status
        self.team_two_scores = team_two_scores

    def GetMatchString(self):
        result_dict = {}
        result_dict[self.team_one] = self.team_one_scores
        result_dict[self.team_two] = self.team_two_scores
        return result_dict
