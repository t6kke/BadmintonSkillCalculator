import sys

from excelparser import ExcelParser
from teamhandler import TeamHandler, Team


txt_data_games_filename = "test_data.txt" # in the future it will have some spreadsheet as input so this is just for basic testing
excel_data_games_filename = "mm_test_data.xlsx" # excel example
verbose=False

def main():
    all_games_list = [] #TODO move back to initial variable
    handleLaunchArguments(sys.argv)
    
    print("\nBadminton Skill Calculator")
    print("prototype v1\n")

    #getGames_txt()

    all_games_list_fromExcel = getGames_xlsx(excel_data_games_filename) #TODO ability to read multipel sheets
    all_games_list_withTeams, all_teams_list = convertGameTeamToTeam(all_games_list_fromExcel)


    # just for checking if all games are read in
    #TODO better printout of games list function
    #printAllGames(all_games_list_fromExcel)
    #for game in all_games_list_withTeams:
        #for k,v in game.items():
            #print(type(k), k, type(v), v)


    #calculateAndPresentResults(all_games_list)
    calculateAndPresentResults(all_games_list_withTeams, all_teams_list)

    # code finished
    print("=====================\nDone")


def handleLaunchArguments(launch_arguments):
    pass #TODO do lauch arguments handling

def getGames_txt():
    with open(txt_data_games_filename, "r") as game_data:
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
                    all_games_list.append(set_one_dict)
                    all_games_list.append(set_two_dict)
                    set_one_dict = {}
                    set_two_dict = {}
                row_counter += 1

def getGames_xlsx(excel_data_games_filename):
    excelParser = ExcelParser(excel_data_games_filename, "Sheet1")
    t_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
    print(t_name)

    excelParser.collectGames()

    all_games_list = excelParser.getGames()

    excelParser2 = ExcelParser(excel_data_games_filename, "Sheet2")
    t_name2 = excelParser2.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
    print(t_name2)

    excelParser2.collectGames()

    all_games_list = all_games_list + excelParser2.getGames()

    return all_games_list

def calculateAndPresentResults(all_games_list, all_teams_list):
    if len(all_games_list) == 0:
        raise Exception("no games found exception")
    teamHandler = TeamHandler(all_teams_list, verbose)
    
    #TODO team entry not needed here anymore, it's done when games are extracted from excel
    # insert content into skill calculator
    #for game in all_games_list:
        #for item in game:
            #teamHandler.addTeam(item)
    
    #print("Base data:")
    #teamHandler.reportTeamData()
    
    # run calculations
    for game in all_games_list:
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

def printAllGames(all_games_list):
    print("All games:")
    for game in all_games_list:
        print(game)
    print("\n")

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


main()
