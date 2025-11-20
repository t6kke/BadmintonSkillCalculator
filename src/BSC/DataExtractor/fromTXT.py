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
                if line.startswith("Match"):
                    pass # used to print out game numbers from source
                elif line.startswith("\n"):
                    pass # ignore empty lines
                else:
                    split_line = line.rstrip().split("\t")

                    comp_one_data = split_line[0]
                    comp_two_data = split_line[1]

                    #print(row_counter, comp_one_data, comp_two_data)

                    comp_one_team_name = comp_one_data.split(" ")[0]
                    comp_one_scores = comp_one_data.split(" ")[1].split(":")
                    comp_two_team_name = comp_two_data.split(" ")[0]
                    comp_two_scores = comp_two_data.split(" ")[1].split(":")

                    #print(row_counter, comp_one_team_name, comp_one_scores, comp_two_team_name, comp_two_scores)

                    set_one_dict[comp_one_team_name] = comp_one_scores
                    set_two_dict[comp_two_team_name] = comp_two_scores
                    if row_counter % 2 == 0:
                        comp_one_data = split_line[0]
                        comp_two_data = split_line[1]

                        comp_one_team_name = comp_one_data.split(" ")[0]
                        comp_one_scores = comp_one_data.split(" ")[1].split(":")
                        comp_two_team_name = comp_two_data.split(" ")[0]
                        comp_two_scores = comp_two_data.split(" ")[1].split(":")

                        set_one_dict[comp_one_team_name] = comp_one_scores
                        set_two_dict[comp_two_team_name] = comp_two_scores

                        result_games_list.append(set_one_dict)
                        result_games_list.append(set_two_dict)
                        set_one_dict = {}
                        set_two_dict = {}
                    row_counter += 1
    return result_games_list
