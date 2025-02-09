import sys

from excelparser import ExcelParser
from teamhandler import TeamHandler


txt_data_games_filename = "test_data.txt" # in the future it will have some spreadsheet as input so this is just for basic testing
excel_data_games_filename = "mm_test_data.xlsx" # excel example
verbose=False

def main():
    all_games_list = [] #TODO move back to initial variable
    handleLaunchArguments(sys.argv)
    
    print("\nBadminton Skill Calculator")
    print("prototype v1\n")

    #getGames_txt()

    all_games_list = getGames_xlsx(excel_data_games_filename) #TODO ability to read multipel sheets

    # just for checking if all games are read in 
    printAllGames(all_games_list)

    calculateAndPresentResults(all_games_list)

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
    excelParser = ExcelParser(excel_data_games_filename)
    t_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
    print(t_name)

    excelParser.collectGames()

    all_games_list = excelParser.getGames()
    return all_games_list

def calculateAndPresentResults(all_games_list):
    if len(all_games_list) == 0:
        raise Exception("no games found exception")
    teamHandler = TeamHandler(verbose) 
    
    # insert content into skill calculator
    for game in all_games_list:
        for item in game:
            teamHandler.addTeam(item)
    
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



main()