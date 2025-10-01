import re
import sys
import os.path
import json

from BSC.DataExtractor.fromTXT import getGamesFromTXT
from BSC.DataExtractor.fromExcel import ExcelParser
from BSC.GameHandler.handler import Handler
from BSC.Utils.handleargs import HandleArgs
from BSC.Utils.commands import Argument, Command, arguments_info, commands_info
from BSC.Utils.output import Output
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
        self.command_arg_objects_dict = {}
        self.__registerCommands()
        self.__ExecuteApp()


    def __registerCommands(self):
        db_name = Argument("--db_name", arguments_info.get("--db_name"), is_mandatory=True)
        excel_file = Argument("--file", arguments_info.get("--file"), "-f", is_mandatory=True)
        excel_sheet = Argument("--sheet", arguments_info.get("--sheet"), "-s", is_mandatory=True)
        c_name = Argument("--c_name", arguments_info.get("--c_name"), is_mandatory=True, function=self.argFuncAddCategory)
        c_desc = Argument("--c_desc", arguments_info.get("--c_desc"), is_mandatory=True)
        output_type = Argument("--out", arguments_info.get("--out"), "-o")
        verbose = Argument("--verbose", arguments_info.get("--verbose"), "-v")
        help_arg = Argument("--help", arguments_info.get("--help"), "-h")
        list_category_options = Argument("--list", arguments_info.get("--list"), "-l", function=self.argFuncListCategories)
        list_report_options = Argument("--list", arguments_info.get("--list"), "-l", function=self.argFuncListReports)
        report_name = Argument("--r_name", arguments_info.get("--r_name"), function=self.argFuncRunReport)
        report_tid_filter = Argument("--r_tidf", arguments_info.get("--r_tidf"))

        self.commands["version"] = Command("version", commands_info.get("version"), self.commandVersion)
        self.commands["help"] = Command("help", commands_info.get("help"), self.commandHelp) #TODO initial help should also be both '-h' and '--help'
        self.commands["insert"] = Command("insert", commands_info.get("insert"), self.commandInsert, db_name=db_name, excel_file=excel_file, excel_sheet=excel_sheet, c_name=c_name, c_desc=c_desc, output_type=output_type, verbose=verbose, help_arg=help_arg)
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
        output_type = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("output_type").arg_options)
        self.output = Output(output_type)
        self.output.write(self.verbose, "INFO", None, name="Badminton Skill Calculator")
        self.output.write(self.verbose, "INFO", None, version=self.app_version)
        launch_command.run()
        self.__exitSuccess("\n=====================\nDone")


    def commandVersion(self):
        print("  Badminton Skill Calculator")
        print(f"  version: {self.app_version}\n")

    def commandHelp(self):
        for args_dict in self.commands.values():
            print(args_dict)
            for arg in args_dict.kv_arguments.values():
                print(arg)
            print("")

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
        source_file = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("excel_file").arg_options) #TODO handle no value provided by user
        sheets_list = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("excel_sheet").arg_options) #TODO handle no value provided by user
        category_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_name").arg_options) #TODO handle no value provided by user
        category_desc = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_desc").arg_options) #TODO handle no value provided by user
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        raw_tournaments_from_excel = self.__getGamesFromExcel(source_file, sheets_list)
        gamesHandler = Handler(self.database_obj, self.verbose)
        category_id = self.database_obj.GetOrAddCategory(category_name, category_desc)
        tournament_id = None
        for tournament_name_data, raw_matches_list_from_excel in raw_tournaments_from_excel.items():
            tournament_date = re.search("(\d{2}\.\d{2}\.\d{4})", tournament_name_data).group()
            tournament_location = re.search("@([^)]+)", tournament_name_data).group().lstrip("@")
            tournament_name = tournament_name_data.split("(")[0].strip()
            print(f"\nStarting handle tournament: '{tournament_name}' information...")
            if self.verbose: print(f"INFO --- Checking if '{tournament_name}' exists in DB")
            tournament_data = self.database_obj.FindTournament(tournament_name, tournament_date)
            if len(tournament_data) != 0:
                tournament_id = tournament_data[0][0]
                print(f"INFO --- Tournament '{tournament_name}' already exists in database, not adding")
                continue
            if self.verbose: print(f"INFO --- Adding tournament: '{tournament_name}' to the database")
            tournament_id = self.database_obj.AddTournament((tournament_name, tournament_date, tournament_location))
            if self.verbose: print(f"INFO --- Getting or adding new category to the database")
            print(f"Running games handler functionality...")
            gamesHandler.runGamesParser(raw_matches_list_from_excel, tournament_id, category_id)
            if self.verbose: print(f"Post matches data entry status report")
            #self.database_obj.report_TournamentResult(tournament_id)
        if self.verbose: print(f"Final reports")
        self.database_obj.report_TournamentResult(tournament_id)
        #self.database_obj.report_AllPlayersELOrankOnCategory(category_id)
        #self.database_obj.report_AllPlayersELOrank()
        #self.database_obj.ss_AllPlayersELOrank()

    def argFuncListReports(self):
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        reports_list = self.database_obj.GetAvailableReports()
        self.output.write(self.verbose, "INFO", [], info="Available reports:")
        for report in reports_list:
            self.output.write(self.verbose, "INFO", ["reports"], name=report)
        self.output.PrintResult()

    def argFuncRunReport(self):
        report_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("report_name").arg_options)
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options) #TODO handle no value provided by user
        self.database_obj = DB(db_name, self.output, verbose=self.verbose)
        match report_name: #TODO analyze if we can remove this match/case solution, maybe some automatically populated functions **kwargs dictionary on the argument can be a solution
            case "report_ListTournaments":
                self.database_obj.report_ListTournaments()
            case "report_EloStandings":
                self.database_obj.report_AllPlayersELOrank()
            case "report_TournamentResults":
                tournament_id = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("report_tid_filter").arg_options)
                if tournament_id == "": return print("'--r_tidf' filter for tournament is required")
                self.database_obj.report_TournamentResult(tournament_id)
            case _:
                print("no report found") #TODO better response with, potentially with listing options and also error exit

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
        self.output.write(self.verbose, "INFO", [], info="Available categories:")
        for category in categories_data:
            self.output.write(self.verbose, "INFO", ["categories"], ID=category[0], name=category[1], description=category[2])
        self.output.PrintResult()

    def argFuncAddCategory(self):
        category_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_name").arg_options)
        if category_name == None: self.__exitError("no category name provided, cannot add new category")
        category_desc = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("c_desc").arg_options)
        if category_desc == None: self.__exitError("no category description provided, cannot add new category")
        db_name = self.args_handler.getUsedArgValue(self.command_arg_objects_dict.get("db_name").arg_options)
        self.database_obj = DB(db_name, verbose=self.verbose)
        self.database_obj.GetOrAddCategory(category_name, category_desc)

    def __handleLaunchArgs(self):
        if "--verbose" in self.launch_args_list and "-h" not in self.launch_args_list and "--help" not in self.launch_args_list: #TODO needs to be changed in a way that verbose can be enalbed while also asking help
            self.verbose = True
            print(f"INFO --- Verbose output is enabled")
        if self.verbose: print(f"Handling lauch arguments\nArguments: {str(self.launch_args_list)}")
        self.args_handler = HandleArgs(self.launch_args_list, self.verbose)
        if self.args_handler.wasHelpRequested(): self.__exitSuccess()   # don't run any longer if user asked for help about arguments/program

    def __getGamesFromExcel(self, excel_file, list_of_sheets):
        result_dict = {}
        for sheet in list_of_sheets:
            excelParser = ExcelParser(excel_file, sheet, self.verbose)
            tournament_name = excelParser.getTournamentName() #TODO gets just basic name from the filed, do addtional parsing to extract date and location
            excelParser.collectGames()
            result_dict[tournament_name] = excelParser.getGames()
        return result_dict

    def __exitError(self, message):
        self.output.write(False, "INFO", None, name=message)
        sys.exit(1)

    def __exitSuccess(self, message = None):
        if message == None:
            sys.exit(0)
        self.output.write(False, "INFO", None, name=message)
        sys.exit(0)


if __name__=="__main__":
    if len(sys.argv) <= 1:
        main = Main(sys.argv[1:], verbose=True)     #running the code with no arguments will always be verbose
    else:
        main = Main(sys.argv[1:])
