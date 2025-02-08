from teamhandler import TeamHandler

all_games_list = []

def main():
    print("\nBadminton Skill Calculator")
    print("prototype v1\n")
    
    game_filename = "test_data.txt" # in the future it will have some spreadsheet as input so this is just for basic testing
    
    with open(game_filename, "r") as game_data:
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

    # just for checking if all games are read in 
    #printAllGames()
    
    # basic calculator before implementing some external lib soltuion
    teamHandler = TeamHandler(verbose=True) #TODO make verbose a variable, maybe modifiable with launch parameter
    
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
    print("=====================\nDone")
    

def printAllGames():
    print("All games:")
    for game in all_games_list:
        print(game)
    print("\n")



main()