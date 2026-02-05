import re
import sys
import os.path
import json

from BSC.DataExtractor.fromTXT import getGamesFromTXT
from BSC.DataExtractor.fromExcel import ExcelParser
from BSC.DataExtractor.fromTS import WebScraper
from BSC.GameHandler.handler import Handler
from BSC.Utils.handleargs import HandleArgs
from BSC.Utils.commands import Argument, Command, arguments_info, commands_info
from BSC.Utils.output import Output
from BSC.Database.db import DB

class Main():
    def __init__(self, launch_args_list, verbose=False):
        self.app_version = "alpha 5"
        self.verbose = verbose
        self.test_execution = False
        self.test_data_txt = "test_data.txt"

        self.database_obj = None
        self.launch_args_list = launch_args_list
        self.args_handler = None
        self.commands = {}
        self.command_arg_objects_dict = {}
        self.__registerCommands()
        self.__ExecuteApp()


    def __registerCommands(self):
        db_name = Argument("--db_name", arguments_info.get("--db_name"), is_mandatory=True)
        url_source = Argument("--url", arguments_info.get("--url"), "-u", function=self.argFuncParseURL)
        excel_file = Argument("--file", arguments_info.get("--file"), "-f", function=self.argFuncParseExcel)
        excel_sheet = Argument("--sheet", arguments_info.get("--sheet"), "-s")
        c_name = Argument("--c_name", arguments_info.get("--c_name"), function=self.argFuncAddCategory)
        c_desc = Argument("--c_desc", arguments_info.get("--c_desc"))
        output_type = Argument("--out", arguments_info.get("--out"), "-o")
        verbose = Argument("--verbose", arguments_info.get("--verbose"), "-v")
        help_arg = Argument("--help", arguments_info.get("--help"), "-h")
        list_category_options = Argument("--list", arguments_info.get("--list"), "-l", function=self.argFuncListCategories)
        list_report_options = Argument("--list", arguments_info.get("--list"), "-l", function=self.argFuncListReports)
        report_name = Argument("--r_name", arguments_info.get("--r_name"), function=self.argFuncRunReport)
        report_tid_filter = Argument("--r_tidf", arguments_info.get("--r_tidf"))

        self.commands["version"] = Command("version", commands_info.get("version"), self.commandVersion)
        self.commands["help"] = Command("help", commands_info.get("help"), self.commandHelp) #TODO initial help should also be both '-h' and '--help'
        self.commands["insert"] = Command("insert", commands_info.get("insert"), self.commandInsert, db_name=db_name, url_source=url_source, excel_file=excel_file, excel_sheet=excel_sheet, c_name=c_name, c_desc=c_desc, output_type=output_type, verbose=verbose, help_arg=help_arg)
        self.commands["report"] = Command("report", commands_info.get("report"), self.commandReport, db_name=db_name, list_report_options=list_report_options, report_name=report_name, report_tid_filter=report_tid_filter, output_type=output_type, verbose=verbose, help_arg=help_arg)
        self.commands["category"] = Command("category", commands_info.get("category"), self.commandCategory, db_name=db_name, list_category_options=list_category_options, c_name=c_name, c_desc=c_desc, output_type=output_type, verbose=verbose, help_arg=help_arg)


    def __ExecuteApp(self):
        if len(self.launch_args_list) == 0:
            self.__runTest()
        launch_command = self.commands.get(self.launch_args_list[0].lower())
        if launch_command == None:
            self.__exitError(f"invalid command, options: {list(self.commands.keys())}")
        self.command_arg_objects_dict.update(launch_command.kv_arguments)
        self.__handleLaunchArgs()
        o_type = []
        if self.command_arg_objects_dict.get("output_type") != None:
            o_type = self.command_arg_objects_dict.get("output_type").arg_options
        output_type = self.args_handler.getUsedArgValue(o_type)
        self.output = Output(output_type)
        self.output.write(None, "INFO", None, name="Badminton Skill Calculator")
        self.output.write(None, "INFO", None, version=self.app_version)
        launch_command.run()
        self.__exitSuccess("\n=====================\nDone")


    def commandVersion(self):
        pass #TODO figure out what to do with this, what additional data should be here? Maybe when DB has app metadata it should be provided with the 'version' command

    def commandHelp(self):
        for args_dict in self.commands.values():
            self.output.write(None, "INFO", None, message=args_dict)
            for arg in args_dict.kv_arguments.values():
                self.output.write(None, "INFO", None, message=arg)
            self.output.write(None, "INFO", None, message="")

    def commandReport(self):
        is_executed = False
        for used_arg in self.args_handler.used_args_list:
            if is_executed == True: break
            for reg_arg in self.command_arg_objects_dict.values():
                if used_arg in reg_arg.arg_options:
                    if reg_arg.run != None:
                        is_executed = True
                        reg_arg.run()
                        break

    def commandInsert(self):
        #TODO better handling to switch between inserting data from web or from excel
        url_arg_values = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("url_source").arg_options)
        excel_arg_values = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("excel_file").arg_options)
        if url_arg_values != None:
            self.output.write(True, "INFO", None, message="URL parsing...")
            self.command_arg_objects_dict.get("url_source").run()
        elif excel_arg_values != None:
            self.output.write(True, "INFO", None, message="Excel file parsing...")
            self.command_arg_objects_dict.get("excel_file").run()
        else:
            self.__exitError("Missing either --file or --url argument information, nothing to parse")

    def argFuncParseURL(self):
        url_list = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("url_source").arg_options)
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options)
        database_obj = DB(db_name, self.output, verbose=self.verbose, add_default_categories=True, add_default_leagues=True)
        gamesHandler = Handler(database_obj, self.output, verbose=self.verbose)
        for url in url_list:
            self.output.write(True, "INFO", "tournaments", message=f"Scraping data from web...")
            try:
                scraper = WebScraper(url, self.output, verbose=self.verbose)
            except Exception as e:
                self.output.write(None, "INFO", "tournaments", message=f"URL: '{url}' insert", status="error", error=f"INFO --- problem parsing URL: {e}")
                continue
            matches_list = scraper.rawMatchesObjects_list
            if len(matches_list) == 0:
                self.output.write(None, "INFO", "tournaments", message=f"URL: '{url}' insert", status="error", error=f"INFO --- 0 matches found in given tournament, not adding to the system")
                continue
            tournament_name = scraper.tournament_title
            tournament_location = scraper.tournament_location
            tournament_start_date = scraper.tournament_start
            tournament_end_date = scraper.tournament_end
            self.output.write(True, "INFO", "tournaments", message=f"\nStarting handle tournament: '{tournament_name}' information...")
            self.output.write(True, "INFO", "tournaments", message=f"Checking if '{tournament_name}' exists in DB")
            tournament_data = database_obj.FindTournament(tournament_name, tournament_start_date)
            if len(tournament_data) != 0:
                tournament_id = tournament_data[0][0]
                self.output.write(None, "INFO", "tournaments", message=f"Tournament: '{tournament_name}' insert", status="error", error=f"INFO --- Tournament '{tournament_name}' already exists in database, not adding")
                continue
            self.output.write(True, "INFO", "tournaments", message=f"Adding tournament: '{tournament_name}' to the database")
            tournament_id = database_obj.AddTournament((tournament_name, tournament_start_date, tournament_end_date, tournament_location, url, False))
            self.output.write(True, "INFO", "tournaments", message=f"Running games handler functionality...")
            gamesHandler.runHandler(matches_list, tournament_id)
            self.output.write(None, "INFO", "tournaments", message=f"Tournament: '{tournament_name}' insert", status="success")
        self.output.PrintResult()

    def argFuncParseExcel(self):
        league_name = "custom league"
        league_desc = "Custom league value that is not really relevant for excel based round robin tournaments, default starting ELO is 1000"
        source_file = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("excel_file").arg_options)
        sheets_list = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("excel_sheet").arg_options) #TODO handle no value provided by user
        category_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_name").arg_options) #TODO handle no value provided by user
        category_desc = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_desc").arg_options) #TODO handle no value provided by user
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        raw_tournaments_from_excel = self.__getGamesFromExcel(source_file, sheets_list, category_name, league_name)
        gamesHandler = Handler(self.database_obj, self.output, self.verbose)
        self.database_obj.GetOrAddCategory(category_name, category_desc)
        self.database_obj.AddCustomLeague(league_name, league_desc)
        tournament_id = None
        for tournament_name_data, raw_matches_obj_list_from_excel in raw_tournaments_from_excel.items():
            tournament_date = re.search("(\\d{2}\\.\\d{2}\\.\\d{4})", tournament_name_data).group()
            tournament_location = re.search("@([^)]+)", tournament_name_data).group().lstrip("@")
            tournament_name = tournament_name_data.split("(")[0].strip()
            self.output.write(True, "INFO", "tournaments", message=f"\nStarting handle tournament: '{tournament_name}' information...")
            self.output.write(True, "INFO", "tournaments", message=f"Checking if '{tournament_name}' exists in DB")
            tournament_data = self.database_obj.FindTournament(tournament_name, tournament_date)
            if len(tournament_data) != 0:
                tournament_id = tournament_data[0][0]
                self.output.write(None, "INFO", "tournaments", message=f"Tournament: '{tournament_name}' insert", status="error", error=f"INFO --- Tournament '{tournament_name}' already exists in database, not adding")
                continue
            self.output.write(True, "INFO", "tournaments", message=f"Adding tournament: '{tournament_name}' to the database")
            tournament_id = self.database_obj.AddTournament((tournament_name, tournament_date, tournament_date, tournament_location, None, True))
            self.output.write(True, "INFO", "tournaments", message=f"Running games handler functionality...")
            gamesHandler.runHandler(raw_matches_obj_list_from_excel, tournament_id)
            self.output.write(None, "INFO", "tournaments", message=f"Tournament: '{tournament_name}' insert", status="success")
        self.output.PrintResult()

    def argFuncListReports(self):
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        reports_list = self.database_obj.GetAvailableReports()
        self.output.write(None, "INFO", None, message="Available reports:")
        for report in reports_list:
            self.output.write(None, "INFO", "reports", name=report)
        self.output.PrintResult()

    def argFuncRunReport(self):
        report_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("report_name").arg_options)
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        match report_name: #TODO analyze if we can remove this match/case solution, maybe some automatically populated functions **kwargs dictionary on the argument can be a solution
            case "report_ListAllTournaments":
                self.database_obj.report_ListAllTournaments()
            case "report_ListInternalResultTournaments":
                self.database_obj.report_ListInternalResultTournaments()
            case "report_EloStandings":
                self.database_obj.report_AllPlayersELOrank()
            case "report_TournamentResults":
                tournament_id = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("report_tid_filter").arg_options)
                if tournament_id == "" or tournament_id == None:
                    self.output.write(None, "INFO", None, status="error", message="'--r_tidf' filter for tournament is required")
                    self.output.PrintResult() #TODO should also do error exit?
                    return
                self.database_obj.report_TournamentResult(tournament_id)
            case _:
                self.output.write(None, "INFO", None, status="error", message="report not found") #TODO better response with, potentially with listing options and also error exit
                self.output.PrintResult()

    def commandCategory(self):
        for used_arg in self.args_handler.used_args_list:
            for reg_arg in self.command_arg_objects_dict.values():
                if used_arg in reg_arg.arg_options:
                    if reg_arg.run != None:
                        reg_arg.run()

    def argFuncListCategories(self):
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options)
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        categories_data = self.database_obj.GetAvailableCategories()
        self.output.write(None, "INFO", None, message="Available categories:")
        for category in categories_data:
            self.output.write(None, "INFO", "categories", ID=category[0], name=category[1], description=category[2])
        self.output.PrintResult()

    def argFuncAddCategory(self):
        category_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_name").arg_options)
        if category_name == None: self.__exitError("no category name provided, cannot add new category")
        category_desc = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_desc").arg_options)
        if category_desc == None: self.__exitError("no category description provided, cannot add new category")
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options)
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        category_id = self.database_obj.GetOrAddCategory(category_name, category_desc)
        if category_id == None:
            self.output.write(None, "INFO", None, status="error", message="failed to add category")
        else:
            self.output.write(None, "INFO", None, status="success", message="category added successfully")
        self.output.PrintResult()

    def __handleLaunchArgs(self):
        if "--verbose" in self.launch_args_list and "-h" not in self.launch_args_list and "--help" not in self.launch_args_list: #TODO needs to be changed in a way that verbose can be enalbed while also asking help
            self.verbose = True
            print(f"INFO --- Verbose output is enabled")
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        self.args_handler = HandleArgs(self.launch_args_list, self.verbose)
        if self.args_handler.wasHelpRequested(): self.__exitSuccess()   # don't run any longer if user asked for help about arguments/program

    def __getGamesFromExcel(self, excel_file, list_of_sheets, category_name, league_name):
        result_dict = {}
        for sheet in list_of_sheets:
            excelParser = ExcelParser(excel_file, sheet, category_name, league_name, self.output, self.verbose)
            tournament_name = excelParser.getTournamentName()
            excelParser.collectGames()
            result_dict[tournament_name] = excelParser.getRawMatchesObjList()
        return result_dict

    def __exitError(self, message):
        self.output.write(None, "ERROR", None, error=message)
        sys.exit(1)

    def __exitSuccess(self, message = None):
        if message == None:
            sys.exit(0)
        self.output.write(None, "INFO", None, message=message)
        sys.exit(0)

    def __runTest(self):
        verbose = False

        #Testing execution with reading txt file
        # tournament_name = "Example Tournament"
        # tournament_date = "2025-12-01"
        # tournament_location = "Example Location"
        # category_name = "EC"
        # category_desc = "example category"
        # league_name = "example league"
        # league_desc = "example league"
        # db_name = "db_txt.db"
        # matches_list = getGamesFromTXT(self.test_data_txt, category_name, league_name)
        # output = Output("console")
        # database_obj = DB(db_name, output, verbose=verbose, clear_db=True)
        # gamesHandler = Handler(database_obj, output, verbose=verbose)
        # category_id = database_obj.GetOrAddCategory(category_name, category_desc)
        # database_obj.AddCustomLeague(league_name, league_desc)
        # tournament_id = database_obj.AddTournament((tournament_name, tournament_date, tournament_date, tournament_location, None, True))
        # gamesHandler.runHandler(matches_list, tournament_id)
        # output.write(verbose, "INFO", None, message=f"Final reports")
        # database_obj.report_TournamentResult(tournament_id)
        # database_obj.report_AllPlayersELOrank()

        #Testing execution with scraping tournamentsoftware.com
        test_url_1 = "https://www.tournamentsoftware.com/tournament/dd30e793-b978-4ad4-83cb-3459de20b11b"
        test_url_2 = "https://www.tournamentsoftware.com/tournament/FA21631F-AB1E-49B0-80C3-C67CAB546CBB"
        test_url_list = [test_url_1, test_url_2]

        faulty_league = "https://www.tournamentsoftware.com/tournament/A00B514B-32A7-4D53-BFFB-4C27AFDBFACC"
        test_url_list = [faulty_league]

        # gp_1 = "https://www.tournamentsoftware.com/tournament/4C2B2BAC-8BBA-4586-B842-10C444F8B13C"
        # gp_2 = "https://www.tournamentsoftware.com/tournament/FA21631F-AB1E-49B0-80C3-C67CAB546CBB"
        # ava_voistlus = "https://www.tournamentsoftware.com/tournament/A53C2D0E-E068-4995-8D2F-8D295C535A11"
        # lining_1 = "https://www.tournamentsoftware.com/tournament/8A2817D9-B25B-466A-9FFB-6BE782B3301A"
        # young_1 = "https://www.tournamentsoftware.com/tournament/58727CE6-C7FF-4505-BA88-B0D2B5D05CB3"
        # victor_1 = "https://www.tournamentsoftware.com/tournament/63C4E8DC-6995-4500-8FD4-82C12285E77B"
        # young_2 = "https://www.tournamentsoftware.com/tournament/DEE3D39A-C0DA-4B1E-A0CC-C01921C90D77"
        # lining_2 = "https://www.tournamentsoftware.com/tournament/DD30E793-B978-4AD4-83CB-3459DE20B11B"
        # young_3 = "https://www.tournamentsoftware.com/tournament/170E0FF4-AF94-4F2A-B9A0-C0D8654195BB"
        # test_url_list = [gp_1, gp_2, ava_voistlus, lining_1, young_1, victor_1, young_2, lining_2, young_3]

        #database_obj = None
        output = Output("console")
        db_name = "db_tournamentsoftware_test.db"
        database_obj = DB(db_name, output, verbose=verbose, add_default_categories=True, add_default_leagues=True, clear_db=True)
        for test_url in test_url_list:

            scraper = WebScraper(test_url, output, database_obj, verbose=verbose)
            matches_list = scraper.rawMatchesObjects_list
            if len(matches_list) == 0:
                print("0 matches found in the given tournament, will skip")
                continue
            tournament_name = scraper.tournament_title
            tournament_location = scraper.tournament_location
            tournament_start_date = scraper.tournament_start
            tournament_end_date = scraper.tournament_end

            #gamesHandler = Handler(database_obj, output, verbose=verbose)
            #tournament_id = database_obj.AddTournament((tournament_name, tournament_start_date, tournament_end_date, tournament_location, test_url, False))
            #gamesHandler.runHandler(matches_list, tournament_id)
        #database_obj.ss_AllPlayersELOrank()

        sys.exit(0)


if __name__=="__main__":
    if len(sys.argv) <= 1:
        main = Main(sys.argv[1:], verbose=True)     #running the code with no arguments will always be verbose
    else:
        main = Main(sys.argv[1:])
