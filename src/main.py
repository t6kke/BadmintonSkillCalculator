import sys
import os.path

from BSC.DataExtractor.fromTXT import getGamesFromTXT
from BSC.DataExtractor.fromExcel import ExcelParser
from BSC.GameHandler.handler import Handler
from BSC.Utils.handleargs import HandleArgs
from BSC.Utils.commands import Argument, Command, arguments_info, commands_info
from BSC.Database.db import DB

class Main():
    def __init__(self, launch_args_list, verbose=False):
        self.app_version = "alpha 4"
        self.verbose = verbose
        self.test_execution = False
        self.test_data_txt = "test_data.txt"

        self.database_obj = None
        self.launch_args_list = launch_args_list
        self.args_handler = None
        self.commands = {}
        self.__registerCommands()
        self.__newExecute()
        #self.__handleLaunchArgs()

        #final function to run the main functionality
        #self.__execute()


    def __registerCommands(self):
        db_name = Argument("--db_name", arguments_info.get("--db_name"), is_mandatory=True)
        excel_file = Argument("--file", arguments_info.get("--file"), "-f", is_mandatory=True)
        excel_sheet = Argument("--sheet", arguments_info.get("--sheet"), "-s", is_mandatory=True)
        c_name = Argument("--c_name", arguments_info.get("--c_name"), is_mandatory=True)
        c_desc = Argument("--c_desc", arguments_info.get("--c_desc"), is_mandatory=True)
        output_type = Argument("--out", arguments_info.get("--out"), "-o")
        verbose = Argument("--verbose", arguments_info.get("--verbose"), "-v")
        help_arg = Argument("--help", arguments_info.get("--help"), "-h")
        list_options = Argument("--list", arguments_info.get("--list"), "-l", function=self.argFuncListReports)
        report_name = Argument("--r_name", arguments_info.get("--r_name"))
        report_tid_filter = Argument("--r_tidf", arguments_info.get("--r_tidf"))

        self.commands["version"] = Command("version", commands_info.get("version"), self.commandVersion)
        self.commands["help"] = Command("help", commands_info.get("help"), self.commandHelp) #TODO initial help should also be both '-h' and '--help'
        self.commands["insert"] = Command("insert", commands_info.get("insert"), self.commandInsert, db_name, excel_file, excel_sheet, c_name, c_desc, output_type, verbose, help_arg)
        self.commands["report"] = Command("report", commands_info.get("report"), self.TEMP_commandReport, db_name, list_options, report_name, report_tid_filter, help_arg)
        self.commands["category"] = Command("category", commands_info.get("category"), self.commandCategory, db_name, list_options, c_name, c_desc, help_arg)

    def __newExecute(self):
        if len(self.launch_args_list) == 0:
            self.__runTest()
        launch_command = self.commands.get(self.launch_args_list[0].lower())
        if launch_command == None:
            self.__exitError(f"invalid command, options: {list(self.commands.keys())}")
        launch_command.run()
        self.__exitSuccess("\n=====================\nDone")

    def TEMP_commandReport(self):
        self.__newHandleLaunchArgs()

        match self.launch_args_list[1:]:
            case "--list" | "-h":
                print("do reports listing")
            case "--r_name":
                print("do report execution")
            case _:
                print("default case")


    def argFuncListReports(self):
        db_name = self.args_handler.getDatabaseName()
        self.database_obj = DB(db_name, verbose=self.verbose)
        reports = self.database_obj.GetAvailableReports()
        print(type(reports), reports)


    def __newHandleLaunchArgs(self):
        if "--verbose" in self.launch_args_list and "-h" not in self.launch_args_list and "--help" not in self.launch_args_list: #TODO needs to be changed in a way that verbose can be enalbed while also asking help
            self.verbose = True
            print(f"INFO --- Verbose output is enabled")
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        self.args_handler = HandleArgs(self.launch_args_list, self.verbose)
        if self.args_handler.wasHelpRequested(): self.__exitSuccess()   # don't run any longer if user asked for help about arguments/program


    def __handleLaunchArgs(self):
        if "--verbose" in self.launch_args_list and "-h" not in self.launch_args_list and "--help" not in self.launch_args_list: #TODO needs to be changed in a way that verbose can be enalbed while also asking help
            self.verbose = True
            print(f"INFO --- Verbose output is enabled")
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        if len(self.launch_args_list) == 0:
            self.test_execution = True
        self.args_handler = HandleArgs(self.launch_args_list, self.verbose)
        if self.args_handler.wasHelpRequested(): self.__exitSuccess()   # don't run any longer if user asked for help about arguments/program

    def __execute(self):
        print("\n  Badminton Skill Calculator")
        print(f"  version: {self.app_version}\n")
        if self.test_execution:
            self.__runTest()
        else:
            try:
                self.__run()
            except Exception as e:
                self.__exitError(str(e)+"\nError exit")

    # test execution with sample data from txt file
    def __runTest(self):
        self.verbose = False #for testing purpose sometimes I need full debug log for tests sometimes I don't need it
        db_name = "db_test.db"
        self.database_obj = DB(db_name, verbose=self.verbose, clear_db=True)

        if self.verbose: print(f"Executing test run from file {self.test_data_txt}")
        raw_matches_list, tournament_name, tournament_category_name, tournament_category_description = getGamesFromTXT(self.test_data_txt)
        tournament_id = self.database_obj.AddTournament((tournament_name,))
        category_id = self.database_obj.GetOrAddCategory(tournament_category_name, tournament_category_description)
        if self.verbose: print(f"All matches from raw matches list:\n{raw_matches_list}")
        gamesHandler = Handler(self.database_obj, self.verbose)
        gamesHandler.runGamesParser(raw_matches_list, tournament_id, category_id)
        self.database_obj.report_TournamentResult(tournament_id)
        self.database_obj.report_AllPlayersELOrankOnCategory(category_id)
        self.database_obj.ss_AllPlayersELOrank()
        self.__exitSuccess("\n=====================\nDone")

    # actual execution with data provided through launch arguments
    def __run(self):
        excel_file = self.args_handler.getSourceExcelFileName()
        sheets_list = self.args_handler.getExcelSheetsList()
        db_name = self.args_handler.getDatabaseName()
        category_name = self.args_handler.getCategoryName()
        category_desc = self.args_handler.getCategoryDescription()

        if excel_file == "" or len(sheets_list) == 0:
            raise Exception("No valid source data provided exception")
        if db_name == "":
            raise Exception("No valid database name provided")
        if category_name == "" or category_desc == "":
            #TODO maybe instead of exception user should be prompted for values, and maybe even given options from DB for selection
            raise Exception("No category details provoided")

        self.database_obj = DB(db_name, verbose=self.verbose)
        raw_tournaments_from_excel = self.__getGamesFromExcel(excel_file, sheets_list)
        gamesHandler = Handler(self.database_obj, self.verbose)
        category_id = self.database_obj.GetOrAddCategory(category_name, category_desc)
        for tournament_name, raw_matches_list_from_excel in raw_tournaments_from_excel.items():
            print(f"\nStarting handle tournament: '{tournament_name}' information...")
            if self.verbose: print(f"INFO --- Adding tournament: '{tournament_name}' to the database")
            tournament_id = self.database_obj.AddTournament((tournament_name,))
            if self.verbose: print(f"INFO --- Getting or adding new category to the database")
            print(f"Running games handler functionality...")
            gamesHandler.runGamesParser(raw_matches_list_from_excel, tournament_id, category_id)
            if self.verbose: print(f"Post matches data entry status report")
            self.database_obj.report_TournamentResult(tournament_id)

        if self.verbose: print(f"Final reports")
        self.database_obj.report_AllPlayersELOrankOnCategory(category_id)
        self.database_obj.report_AllPlayersELOrank()
        self.database_obj.ss_AllPlayersELOrank()
        self.__exitSuccess("\n=====================\nDone")

    def __getGamesFromExcel(self, excel_file, list_of_sheets):
        result_dict = {}
        for sheet in list_of_sheets:
            excelParser = ExcelParser(excel_file, sheet, self.verbose)
            tournament_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
            excelParser.collectGames()
            result_dict[tournament_name] = excelParser.getGames()
        return result_dict

    def commandVersion(self):
        print("  Badminton Skill Calculator")
        print(f"  version: {self.app_version}\n")

    def commandHelp(self):
        for k,v in self.commands.items():
            print(v)
            for arg in v.arguments:
                print(arg)
            print("")

    def commandInsert(self):
        #TODO code here
        pass

    def commandReport(self):
        #TODO code here
        pass

    def commandCategory(self):
        #TODO code here
        pass

    def commandTest(self):
        print("hello from command")

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
