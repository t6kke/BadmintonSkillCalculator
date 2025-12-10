from BSC.GameHandler.rawmatch import RawMatch

#for inital development and testing, intended for the 'test_data.txt' file parsing and extracting list of games dictionaries.
#TODO add verbose option but very low priority.
def getGamesFromTXT(txt_data_games_filename):
    result_rawGameObj_list = []
    with open(txt_data_games_filename, "r") as game_data:
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

                comp_one_team_name = comp_one_data.split(" ")[0]
                comp_one_scores = comp_one_data.split(" ")[1].split(":")
                comp_two_team_name = comp_two_data.split(" ")[0]
                comp_two_scores = comp_two_data.split(" ")[1].split(":")

                if comp_one_scores[-1] > comp_two_scores[-1]:
                    comp_one_status = "W"
                    comp_two_status = None
                else:
                    comp_two_status = "W"
                    comp_one_status = None

                new_raw_match = RawMatch("EC", "example league", comp_one_team_name, comp_one_status, comp_one_scores, comp_two_team_name, comp_two_status, comp_two_scores)
                result_rawGameObj_list.append(new_raw_match)

                if row_counter % 2 == 0:
                    comp_one_data = split_line[0]
                    comp_two_data = split_line[1]

                    comp_one_team_name = comp_one_data.split(" ")[0]
                    comp_one_scores = comp_one_data.split(" ")[1].split(":")
                    comp_two_team_name = comp_two_data.split(" ")[0]
                    comp_two_scores = comp_two_data.split(" ")[1].split(":")

                    if comp_one_scores[-1] > comp_two_scores[-1]:
                        comp_one_status = "W"
                        comp_two_status = None
                    else:
                        comp_two_status = "W"
                        comp_one_status = None

                    new_raw_match = RawMatch("EC", "example league", comp_one_team_name, comp_one_status, comp_one_scores, comp_two_team_name, comp_two_status, comp_two_scores)
                    result_rawGameObj_list.append(new_raw_match)
                row_counter += 1
    return result_rawGameObj_list
