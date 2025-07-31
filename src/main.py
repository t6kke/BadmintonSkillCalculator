import sys
import os.path

from BSC.DataExtractor.fromTXT import getGamesFromTXT
from BSC.DataExtractor.fromExcel import ExcelParser
from BSC.GameHandler.handler import Handler
from BSC.Utils.handleargs import HandleArgs
from BSC.Database.db import DB

class Main():
    def __init__(self, launch_args_list, verbose=False):
        self.verbose = verbose
        self.test_execution = False
        self.test_data_txt = "test_data.txt"

        self.database_obj = None
        self.launch_args_list = launch_args_list
        self.args_handler = None
        self.__handleLaunchArgs()

        #TODO additional class variables if needed
        self.all_games_list = []
        self.all_teams_list = []

        #final function to run the main functionality
        self.__execute()

    def __handleLaunchArgs(self):
        if "--verbose" in self.launch_args_list and "-h" not in self.launch_args_list and "--help" not in self.launch_args_list: #TODO needs to be changed in a way that verbose can be enalbed while also asking help
            self.verbose = True
            print(f"INFO --- Verbose outoput is enabled")
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        if len(self.launch_args_list) == 0:
            self.test_execution = True
        self.args_handler = HandleArgs(self.launch_args_list, self.verbose)
        if self.args_handler.wasHelpRequested(): self.__exitSuccess()   # don't run any longer if user asked for help about arguments/program

    def __execute(self):
        print("\n  Badminton Skill Calculator")
        print("  prototype v3\n")
        if self.test_execution:
            self.__runTest()
        else:
            try:
                self.__run()
            except Exception as e:
                self.__exitError(str(e)+"\nError exit")

    # test execution with sample data from txt file
    def __runTest(self):
        # just initial code to explore db usage
        self.verbose = False #for testing purpose sometimes I need full debug log for tests sometimes I don't need it
        #db_name = self.args_handler.getDatabaseName()
        db_name = "db_test.db"
        self.database_obj = DB(db_name, verbose=self.verbose, clear_db=True)

        if self.verbose: print(f"Executing test run from file {self.test_data_txt}")
        raw_games_list, tournament_name, tournament_category_name, tournament_category_description = getGamesFromTXT(self.test_data_txt)
        tournament_id = self.database_obj.AddTournament((tournament_name,))
        category_id = self.database_obj.GetOrAddCategory(tournament_category_name, tournament_category_description)
        if self.verbose: print(f"All games from raw games list:\n{raw_games_list}")
        gamesHandler = Handler(raw_games_list, self.database_obj, tournament_id, category_id, self.verbose)
        self.database_obj.report_TournamentResult(tournament_id)
        self.database_obj.report_AllUsersELOrank()
        self.__exitSuccess("\n=====================\nDone")

    # actual execution with data provided through launch arguments
    def __run(self):
        excel_file = self.args_handler.getSourceExcelFileName()
        sheets_list = self.args_handler.getExcelSheetsList()
        if excel_file == "" or len(sheets_list) == 0:
            raise Exception("No valid source data provided exception")
        raw_games_list_from_excel = self.__getGamesFromExcel(excel_file, sheets_list) #TODO investigate how to best enter sheet values?
        gamesHandler = Handler(raw_games_list_from_excel, self.verbose)
        gamesHandler.calculateScore()
        gamesHandler.reportFullGamesList()
        gamesHandler.reportFullTeamsList()
        gamesHandler.reportCalculationsResult()

        """for sheet in sheets_list:
            raw_games_list_from_excel = self.__getGamesFromExcel2(excel_file, sheet)
            gamesHandler = Handler(raw_games_list_from_excel, self.verbose) #TODO need to be able to initalize Handler without providing games data and then manually calling the run on each data set without having to reinitialize it since teams list is related to it
            gamesHandler.calculateScore()
            gamesHandler.reportFullGamesList()
            gamesHandler.reportFullTeamsList()
            gamesHandler.reportCalculationsResult()"""

        self.__exitSuccess("\n=====================\nDone")

    def __getGamesFromExcel(self, excel_file, list_of_sheets):
        list_of_games = []
        for sheet in list_of_sheets:
            excelParser = ExcelParser(excel_file, sheet, self.verbose)
            tournament_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
            print(tournament_name) #TODO better presentation of tournament names that will be parsed
            excelParser.collectGames()
            list_of_games = list_of_games + excelParser.getGames()
        return list_of_games

    def __getGamesFromExcel2(self, excel_file, sheet):  #TODO this is the future solution
        list_of_games = []
        excelParser = ExcelParser(excel_file, sheet, self.verbose)
        tournament_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
        print(tournament_name) #TODO better presentation of tournament names that will be parsed
        excelParser.collectGames()
        list_of_games = excelParser.getGames()
        return list_of_games

    def __exitError(self, message):
        print(message)
        sys.exit(1)

    def __exitSuccess(self, message = None):
        if message == None:
            sys.exit(0)
        print(message)
        sys.exit(0)




if __name__=="__main__":
    if len(sys.argv) <= 1:
        main = Main(sys.argv[1:], verbose=True)     #running the code with no arguments will always be verbose
    else:
        main = Main(sys.argv[1:])
