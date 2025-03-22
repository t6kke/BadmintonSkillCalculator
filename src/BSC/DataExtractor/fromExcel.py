import pandas as pd

class ExcelParser():
    def __init__(self, excel_data_games_filename, excel_sheet_name, verbose=False):
        self.verbose = verbose
        self.excel_data_games_filename = excel_data_games_filename
        self.excel_sheet_name = excel_sheet_name
        self.dataframe = None
        self.__setDataframe()
        self.games_dataframe_list = []
        self.collected_games_list = []

    def getTournamentName(self):
        if self.verbose: print(f"INFO --- retreiving tournament name")
        dataframe_event_name = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, nrows=1, header=None)
        event_name = dataframe_event_name.at[0,0]
        #print(pd.ExcelFile(self.excel_data_games_filename).sheet_names)    # sheets can be found like this, not sure if needed
        if self.verbose: print(f"DEBUG --- returning tournament name: '{event_name}'")
        return str(event_name)

    def getGames(self):
        if self.verbose: print(f"INFO --- returning all collected games: '{self.collected_games_list}'")
        return self.collected_games_list

    def collectGames(self):
        if self.verbose: print(f"INFO --- staring collection of games from dataframe:\n{self.dataframe}")
        last_column = self.__findLastGamesColumn()
        last_row = len(self.dataframe.index)-1
        first_game_row = self.__findFirstGamesRow()
        if self.verbose: print(f"DEBUG --- games section limiters -- First game row: '{first_game_row}' -- Last row: '{last_row}' -- Last column: '{last_column}'")

        column_range = [] #Used to limit colums for the game dataframes
        for i in range(0,last_column+1):
            column_range.append(i)
        for i in range(first_game_row,last_row+1,5):    #TODO range step is hardcoded as 5 since it's standard, it could be extraced dynamically but not relevant for now
            self.__getGameDataframe(i,column_range)

        self.__getAllGames()


    def __setDataframe(self):
        if self.verbose: print(f"INFO --- getting the full dataframe from excel")
        self.dataframe = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, header=None)
        if self.verbose: print(f"DEBUG --- got this dataframe:\n{self.dataframe}")

    def __findLastGamesColumn(self):
        for column in range(len(self.dataframe.columns)):
            nan_counter = 0
            for row in range(len(self.dataframe.index)):
                if str(self.dataframe.loc[row].at[column]).lower() == "nan":
                    nan_counter += 1
                else:
                    nan_counter = 0
                if nan_counter > 9:
                    return column-1

    def __findFirstGamesRow(self):
        for row in range(len(self.dataframe.index)):
            val = self.dataframe.loc[row].at[0]
            if str(self.dataframe.loc[row].at[0]).lower().startswith("game"):
                return row

    def __getGameDataframe(self, row_index, column_range):
        if self.verbose: print(f"INFO --- getting specific games section dataframe")
        dataframe = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, skiprows=row_index, nrows=4, usecols=column_range, header=None)
        if self.verbose: print(f"DEBUG --- found this dataframe:\n{dataframe}")
        self.games_dataframe_list.append(dataframe)

    def __getAllGames(self):    #TODO should also add some verbose information to this function
        df_colums = len(self.games_dataframe_list[0].columns)
        for df in self.games_dataframe_list:
            for i in range(0,df_colums,2):
                temp_dict = {}
                team_one = str(df.loc[2].at[i]).rstrip()
                team_two = str(df.loc[3].at[i]).rstrip()
                team_one_score = df.loc[2].at[i+1]
                team_two_score = df.loc[3].at[i+1]
                temp_dict[team_one] = team_one_score
                temp_dict[team_two] = team_two_score
                self.collected_games_list.append(temp_dict)
