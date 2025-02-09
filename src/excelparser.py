import pandas as pd

class ExcelParser():
    def __init__(self, excel_data_games_filename):
        self.excel_data_games_filename = excel_data_games_filename
        self.dataframe = None

    def getTournamentName(self):
        dataframe_event_name = pd.read_excel(self.excel_data_games_filename, nrows=1, header=None)
        #print("Tournament Name: ", dataframe_event_name.at[0,0], "\n")
        return str(dataframe_event_name.at[0,0])
    
    def getGames(self):
        self.dataframe = pd.read_excel(self.excel_data_games_filename, skiprows=[0], header=None)
        print("\n", self.dataframe, "\n")
        last_column = self.__findLastGamesColumn()
        last_row = len(self.dataframe.index)-1
        print("last column with data:", last_column)
        print("last row:", last_row)
    


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