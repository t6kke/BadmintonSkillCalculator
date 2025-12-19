from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import json
import time
import re
import requests
from bs4 import BeautifulSoup

from BSC.GameHandler.rawmatch import RawMatch

URL_PART_SITE = "https://www.tournamentsoftware.com"
URL_PART_MATCHES = "/matches"

class WebScraper():
    def __init__(self, url, output, verbose=False):
        self.verbose = verbose
        self.output = output #TODO build out information printing logic
        self.url = url

        self.tournament_title = ""
        self.tournament_location = ""
        self.tournament_start = ""
        self.tournament_end = ""
        self.rawMatchesObjects_list = []
        self.tounament_days_list = []

        self.__runScraper()


    def __runScraper(self):
        if URL_PART_SITE not in self.url:
            raise Exception("not a supported site URL provided")
        #TODO figure out if we can accept cookies first so I would not have to waste time accepting them on every time I want to visit the page
        self.__getTournamentMetadata()
        self.__getGamesResults()

    def __getTournamentMetadata(self):
        soup = None

        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get('https://www.tournamentsoftware.com/')

            # Accept Cookiewall
            driver.find_element(By.XPATH, '//button[@type="submit"]').click()
            time.sleep(2)

            # Get all cookies
            cookies = driver.get_cookies()
            # Save cookies to file
            with open('selenium_cookies.json', 'w') as f:
                json.dump(cookies, f)

            # Navigate to protected page and get content
            driver.get(self.url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
        finally:
            driver.quit()

        if soup == None:
            raise Exception("Error retreiving data from URL")

        #extracting tournament name
        self.tournament_title = soup.find("h2", class_=["media__title", "media__title--large"]).get_text(strip=True)

        #extracting tournament location
        module_cards = soup.find_all("div", class_=["module", "module--card"])
        for module_card in module_cards:
            mc_title = module_card.find("h3", class_=["module__title"])
            if mc_title == None:
                continue
            if mc_title.get_text(strip=True) != "Venue":
                continue
            media = module_card.find("div", class_=["media"])
            self.tournament_location = media.find("span", class_=["nav-link__value"]).get_text(strip=True)

        #extracting tournament start and end dates and also building list of dates for .../matches/<date> URL
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
            soup = None

            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--disable-dev-shm-usage')
            driver = webdriver.Chrome(options=chrome_options)
            try:
                driver.get('https://www.tournamentsoftware.com/')

                # Accept Cookiewall
                driver.find_element(By.XPATH, '//button[@type="submit"]').click()
                time.sleep(2)

                # Get all cookies
                cookies = driver.get_cookies()
                # Save cookies to file
                with open('selenium_cookies.json', 'w') as f:
                    json.dump(cookies, f)

                # Navigate to protected page and get content
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
            finally:
                driver.quit()

            raw_matches = soup.find_all("div",class_=["match","match--list"])
            for raw_match in raw_matches:
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
                team_one = re.sub(r" .\d.","", team_one).lower().replace("-", " ")
                team_two = re.sub(r" .\d.","", team_two).lower().replace("-", " ")

                for i in range(len(match_results)):
                    if i % 2 == 0:
                        team_one_scores.append(match_results[i].get_text(" ", strip=True))
                    else:
                        team_two_scores.append(match_results[i].get_text(" ", strip=True))

                category = match_header.split(" ", 1)[0]
                league = match_header.split(" ", 1)[1].split("-")[0].strip()

                # print("--- DATA ---")
                # print("header:", match_header)
                # print("category:", category)
                # print("league:", league)
                # print(f"Team: '{team_one}' with result: '{team_one_status}' and game scores '{team_one_scores}'")
                # print(f"Team: '{team_two}' with result: '{team_two_status}' and game scores '{team_two_scores}'")
                # print("")

                new_raw_match = RawMatch(category, league, team_one, team_one_status, team_one_scores, team_two, team_two_status, team_two_scores)

                self.rawMatchesObjects_list.append(new_raw_match)
