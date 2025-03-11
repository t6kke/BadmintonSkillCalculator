import sys
import os.path

from excelparser import ExcelParser
from teamhandler import TeamHandler, Team

#======================================================================
# new implementation using new packages setup
#======================================================================
from BSC.DataExtractor.fromTXT import getGamesFromTXT
from BSC.GameHandler.handler import Handler

class Main_new():
    def __init__(self, launch_args_list, verbose=False):
        self.verbose = verbose
        self.test_execution = False
        self.test_data_txt = "test_data.txt"

        self.launch_args_list = launch_args_list
        self.__handleLaunchArgs()#TODO handle launch arguments values

        #TODO additional class variables if needed
        self.all_games_list = []
        self.all_teams_list = []

        #final function to run the main functionality
        self.__execute()

    def __handleLaunchArgs(self):
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        if len(self.launch_args_list) == 0:
            self.test_execution = True
        #TODO code to handle arguments

    def __execute(self):
        print("\nBadminton Skill Calculator")
        print("prototype v2\n")
        if self.test_execution:
            self.__runTest()
        else:
            self.__run()

    # test execution with sample data from txt file
    def __runTest(self):
        if self.verbose: print(f"Executing test run from file {self.test_data_txt}")
        raw_games_list = getGamesFromTXT(self.test_data_txt)
        if self.verbose: print(f"All games from raw games list:\n{raw_games_list}")
        gamesHandler = Handler(raw_games_list, self.verbose)
        gamesHandler.calculateScore()
        gamesHandler.reportCalculationsResult()

        self.__exitSuccess("\n=====================\nDone")

    # actual execution with valid data
    def __run(self):
        pass

    def __exitError(self, message):
        print(message)
        sys.exit(1)

    def __exitSuccess(self, message = None):
        if message == None:
            sys.exit(0)
        print(message)
        sys.exit(0)

#======================================================================
# old implementation, initial logic
# when using old setup not packaged classes and functions
#======================================================================
class Main():
    def __init__(self, excel_file, verbose=True):
        self.all_games_list = []
        self.all_teams_list = []
        self.txt_data_games_filename = "test_data.txt"
        self.excel_data_games_filename = excel_file
        self.list_of_sheets = []
        self.verbose = verbose
        #TODO handle launch arguments here?
        self.__run()

    def __run(self):
        print("\nBadminton Skill Calculator")
        print("prototype v1\n")

        if self.verbose in ["true", "1", "t", "T", "True", True]:
            self.verbose = True
        else:
            self.verbose = False

        if len(self.list_of_sheets) == 0: #TODO bad implementation, probably have to have it be part of launch aruguments or scan document, check excelparser.py on how to detect
            self.list_of_sheets = ["Sheet1"]

        #initial development using txt file as source
        #all_games_list_fromTXT = self.__getGamesFromTXT()
        #self.all_games_list, self.all_teams_list = convertGameTeamToTeam(all_games_list_fromTXT)
        all_games_list_fromExcel = self.__getGamesFromExcel(self.list_of_sheets) #TODO investigate how to best enter sheet values?
        self.all_games_list, self.all_teams_list = convertGameTeamToTeam(all_games_list_fromExcel)

        #TODO better printout of games list function
        #for game in all_games_list_withTeams:
            #for k,v in game.items():
                #print(type(k), k, type(v), v)

        self.__calculateAndPresentResults()

        # code finished
        print("=====================\nDone")

    def __getGamesFromExcel(self, list_of_sheets):
        list_of_games = []
        for sheet in list_of_sheets: #TODO should list_of_sheet be part of Main vars?
            excelParser = ExcelParser(self.excel_data_games_filename, sheet)
            tournament_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
            print(tournament_name)
            excelParser.collectGames()
            list_of_games = list_of_games + excelParser.getGames()
        return list_of_games

    def __calculateAndPresentResults(self):
        if len(self.all_games_list) == 0:
            raise Exception("no games found exception")
        teamHandler = TeamHandler(self.all_teams_list, self.verbose)

        # run calculations
        for game in self.all_games_list:
            team1 = list(game)[0]
            team2 = list(game)[1]
            if game.get(team1) > game.get(team2):
                teamHandler.calculateScore(team1, team2, 1)
            else:
                teamHandler.calculateScore(team1, team2, 2)

        # present results
        print("Final Calculated data:")
        teamHandler.reportTeamData()
        print("\n")

    #for inital development and testing
    def __getGamesFromTXT(self):
        result_games_list = []
        with open(self.txt_data_games_filename, "r") as game_data:
                set_one_dict = {}
                set_two_dict = {}
                row_counter = 1
                for line in game_data:
                    if line.startswith("Game"):
                        pass # used to print out game numbers from source
                    elif line.startswith("\n"):
                        pass # ignore empty lines
                    else:
                        split_line = line.rstrip().split("\t")
                        #print(new_game_check_nr, game_number, split_line[0], split_line[1])
                        set_one_dict[split_line[0].split(" ")[0]] = split_line[0].split(" ")[1]
                        set_two_dict[split_line[1].split(" ")[0]] = split_line[1].split(" ")[1]
                        if row_counter % 2 == 0:
                            set_one_dict[split_line[0].split(" ")[0]] = split_line[0].split(" ")[1]
                            set_two_dict[split_line[1].split(" ")[0]] = split_line[1].split(" ")[1]
                            result_games_list.append(set_one_dict)
                            result_games_list.append(set_two_dict)
                            set_one_dict = {}
                            set_two_dict = {}
                        row_counter += 1
        return result_games_list




def convertGameTeamToTeam(all_games_list_fromExcel): #TODO this function needs to be broken down and handled somewhere outside of main
    result_games_list = []
    teams_list = []
    for game in all_games_list_fromExcel:
        existing_teams = []
        existing_teams_set_list = []
        #print("parsing game:",game)
        for t in teams_list: #creating existing teams list for duplicate checsk
            existing_teams.append(t)
            existing_teams_set_list.append(t.team_member_set)

        teams_from_dict = game.keys()
        in_list = False
        new_game_dict = {}
        for team in teams_from_dict:
            #print("parsing team:", team)
            player_list = names = team.replace(" ", "").split("+")
            temp_player_set = {player_list[0], player_list[1]}
            new_team = None
            if len(existing_teams_set_list) == 0:
                #print("debug --- no existing games yet", "--- SET being handeld: ", temp_player_set)
                #print("Adding team:", team, "from:", teams_from_dict)
                new_team = Team(team, 1000)
                teams_list.append(new_team)
                existing_teams.append(new_team)
                existing_teams_set_list.append(new_team.team_member_set)
            for i in range(len(existing_teams_set_list)):
                #print("debug --- existing teams check",i, "--- comparing candidate:",temp_player_set," with team from existing:",existing_teams_set_list[i], "--- full set of teams:", existing_teams_set_list)
                if temp_player_set not in existing_teams_set_list:
                    #print("Adding team:", team, "from:", teams_from_dict)
                    new_team = Team(team, 1000)
                    teams_list.append(new_team)
                    existing_teams.append(new_team)
                    existing_teams_set_list.append(new_team.team_member_set)
                else:
                    #print("debug --- I found the team from the list")
                    pass

                #replacing the string team value in the game dict with the actual team object
                #game[existing_teams[i]] = game.pop(team) #TODO can't do it like this, have to create new dict for the game and add teams and results into that'
            if new_team == None:
                #TODO we already have the team created, need to find it and use that to make dictionary
                for i in range(len(teams_list)):
                    #print(teams_list[i].team_member_set)
                    if temp_player_set == teams_list[i].team_member_set:
                        #print("Found the team:", teams_list[i].team_member_set)
                        new_game_dict[teams_list[i]] = game[team]
                        break
                pass
            else:
                #print("debug --- current game team and score:", new_team, game[team], existing_teams)
                new_game_dict[new_team] = game[team]
        result_games_list.append(new_game_dict)
    #print(existing_teams_set_list)
    #print(teams_list)
    #print("returning:",result_games_list)
    return(result_games_list, teams_list)


# old way of starting main
"""if __name__=="__main__":
    if len(sys.argv) > 2:
        main = Main(sys.argv[1], sys.argv[2])
    else:
        main = Main("test_xlsx",verbose=True)"""


# new way of starting main
if __name__=="__main__":
    if len(sys.argv) > 2:
        main = Main_new(sys.argv[1:])
    else:
        main = Main_new(sys.argv[1:], verbose=True)
