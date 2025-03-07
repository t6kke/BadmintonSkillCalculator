import pandas as pd

class ExcelParser():
    def __init__(self, excel_data_games_filename, excel_sheet_name): #TODO implement verbose
        self.excel_data_games_filename = excel_data_games_filename
        self.excel_sheet_name = excel_sheet_name
        self.dataframe = None
        self.__setDataframe()
        self.games_dataframe_list = []
        self.collected_games_list = []

    def getTournamentName(self):
        dataframe_event_name = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, nrows=1, header=None)
        #print("Tournament Name: ", dataframe_event_name.at[0,0], "\n")
        print(pd.ExcelFile(self.excel_data_games_filename).sheet_names) #TODO sheets can be found like this
        return str(dataframe_event_name.at[0,0])

    def getGames(self):
        return self.collected_games_list

    def collectGames(self):
        #print("\n", self.dataframe, "\n")
        last_column = self.__findLastGamesColumn()
        last_row = len(self.dataframe.index)-1
        first_game_row = self.__findFirstGamesRow()
        #print("last column with data:", last_column)
        #print("last row:", last_row)
        #print("games start at row: ", first_game_row)
        #self.__getGameDataframe_temp()

        column_range = [] #Used to limit colums for the game dataframes
        for i in range(0,last_column+1):
            column_range.append(i)
        for i in range(first_game_row,last_row+1,5): #TODO range step is hardcoded as 5 since it's standard, it could be extraced dynamically but not relevant for now
            self.__getGameDataframe(i,column_range)

        self.__getAllGames()


    def __setDataframe(self):
        self.dataframe = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, header=None)
        #print(self.dataframe)

    def __findLastGamesColumn(self):
        for column in range(len(self.dataframe.columns)):
            nan_counter = 0
            for row in range(len(self.dataframe.index)):
                if str(self.dataframe.loc[row].at[column]).lower() == "nan":
                    nan_counter += 1
                else:
                    nan_counter = 0
                if nan_counter > 9:
                    #print("found end colum, last data on column:", column)
                    return column-1

    def __findFirstGamesRow(self):
        for row in range(len(self.dataframe.index)):
            val = self.dataframe.loc[row].at[0]
            if str(self.dataframe.loc[row].at[0]).lower().startswith("game"):
                return row

    def __getGameDataframe(self, row_index, column_range):
        dataframe = pd.read_excel(self.excel_data_games_filename, sheet_name=self.excel_sheet_name, skiprows=row_index, nrows=4, usecols=column_range, header=None)
        self.games_dataframe_list.append(dataframe)

    def __getAllGames(self):
        #print(self.gamesDataframe_list)
        #print("\n", self.gamesDataframe_list[0], "\n")
        df_colums = len(self.games_dataframe_list[0].columns)
        for df in self.games_dataframe_list:
            #print("Game: ", df.loc[0].at[0])
            #print(df)
            for i in range(0,df_colums,2):
                temp_dict = {}
                team_one = str(df.loc[2].at[i]).rstrip()
                team_two = str(df.loc[3].at[i]).rstrip()
                team_one_score = df.loc[2].at[i+1]
                team_two_score = df.loc[3].at[i+1]
                temp_dict[team_one] = team_one_score
                temp_dict[team_two] = team_two_score
                self.collected_games_list.append(temp_dict)
