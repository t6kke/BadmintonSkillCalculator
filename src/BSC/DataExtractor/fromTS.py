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

COOKEIS = {
    "ASP.NET_SessionId": "mf0eemxpvsng500mplkaq3df",
    "euconsent-v2": "CQZ8xwAQZ8xwADsACAENCCFkAP_gAEPgAAhoLstR_G__bWlr-bb3aftkeYxP9_hr7sQxBgbJk24FzLvW7JwXx2E5NAzatqIKmRIAu3TBIQNlHJDURVCgKIgVryDMaEyUoTNKJ6BkiFMRI2NYCFxvm4tjWQCY5vr99lc1mB-N7dr82dzyy6hHn3a5_2S1WJCdIYetDfv8ZBKT-9IEd_x8v4v4_F7pE2-eS1n_pGvp6j9-YnM_dBmxt-bSffzPn__rl_e7X_vd_n37v94XH77v____f_-7___2C7AAJhoVEEZYECAQKBhBAgAUFYQAUCAIAAEgYICAEwYFOQMAF1hMgBACgAGCAEAAIMAAQAAAQAIRABQAQCAACAQKAAMACAICAAgYAAQAWIgEAAIDoGKYEEAgWACRmVQaYEoACQQEtlQgkAwIK4QhFngEECImCgAAAAAKAAAAeCwEJJASoSCALiCaAAAgAAAiBAgQSEmAAKgzRaA8CTqMjTAMHzBIgp0GQBMEZCQaEJvQkHikKIUEGQGhSzAHAAAA.YAAAAAAAAAAA",
    "lvt": "K7yBTRpeL0yYWHKfaj0jjsuUw6KXjNsWYtZqI4DZ/8voA7TbsAjx2BP5W2AGt/T45q5DW6qWMYaYQR+gSr/a7Z5zwFExQOzILqyzlV+tfr522l5OIxKuJrYdsnsNeV93r37lkDjFHHqi6NsVT/HfK0nJcADyZGmA86g7ysK7WiwwUfU3fuaMQoCvoNAYV+C4",
    "st": "l=1033&exp=46349.8850925347&c=1&cp=23&s=2"
}

class WebScraper():
    def __init__(self, url, output, verbose=False):
        self.verbose = verbose
        self.output = output
        self.url = url

        self.tournament_title = ""
        self.matches_list = []

        self.__runScraper()


    def __runScraper(self):
        response = requests.get(self.url, headers = HEADERS, cookies = COOKEIS)
        if response.status_code != 200:
            raise Exception(f"bad response code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        self.tournament_title = soup.find("title").get_text()

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

            # print("--- DATA ---")
            # print("header:", match_header)
            # print(f"Team: '{team_one}' with result: '{team_one_status}' and game scores '{team_one_scores}'")
            # print(f"Team: '{team_two}' with result: '{team_two_status}' and game scores '{team_two_scores}'")
            # print("Final dictionary of the match:")
            # print(match_dict)
            # print("")

            self.matches_list.append(match_dict)
