#for inital development and testing, intended for the 'test_data.txt' file parsing and extracting list of games dictionaries.
#TODO maybe should add verbose option but very low priority.
#TODO maybe logic should be split into separate functions but very low priority.
def getGamesFromTXT(txt_data_games_filename):
    result_games_list = []
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
                        result_games_list.append(set_one_dict)
                        result_games_list.append(set_two_dict)
                        set_one_dict = {}
                        set_two_dict = {}
                    row_counter += 1
    return result_games_list, "Example Tournament From TXT file", "EC", "example category"
