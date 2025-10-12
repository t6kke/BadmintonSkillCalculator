from BSC.Utils.handlehelp import helpSelector

class HandleArgs():
    def __init__(self, args_list, verbose=False):
        #argument values variables to be filled
        self.source_excel = ""
        self.source_excel_sheet_list = []
        self.database_name = ""
        self.output_type = ""
        self.category_name = ""
        self.category_desc = ""
        self.report_name = ""
        self.report_tournament_id_filter = ""
        self.used_args_list = []
        self.used_args_value_dict = {}

        # general class variables
        self.verbose = verbose
        self.args_list = args_list
        self.args_used = []
        self.was_help_requested = False
        #parse arguments on initilization
        self.__handleArgumentsList()


    #============================================
    # variable get functions
    #============================================
    def getUsedArgValue(self, arg_key_list):
        arg_key = None
        arg_value = None
        for arg_key in arg_key_list:
            arg_value = self.used_args_value_dict.get(arg_key)
            if arg_value != None: break
        if self.verbose: print(f"INFO --- argument '{arg_key}' value was requested, returning: '{arg_value}'")
        return arg_value

    def wasHelpRequested(self):
        if self.verbose: print(f"INFO --- help request status info was requested, returning: '{self.was_help_requested}'")
        return self.was_help_requested

    # def __getSourceExcelFileName(self):
    #     if self.verbose: print(f"INFO --- excel file name was requested, returning: '{self.source_excel}'")
    #     return self.source_excel
    #
    # def __getExcelSheetsList(self):
    #     if self.verbose: print(f"INFO --- list of sheets was requested, returning: '{self.source_excel_sheet_list}'")
    #     return self.source_excel_sheet_list
    #
    # def __getDatabaseName(self):
    #     if self.verbose: print(f"INFO --- database info was requested, returning: '{self.database_name}'")
    #     return self.database_name
    #
    # def __getCategoryName(self):
    #     if self.verbose: print(f"INFO --- category name was requested, returning: '{self.category_name}'")
    #     return self.category_name
    #
    # def __getCategoryDescription(self):
    #     if self.verbose: print(f"INFO --- category description was requested, returning: '{self.category_desc}'")
    #     return self.category_desc
    #
    # def __getReportName(self):
    #     if self.verbose: print(f"INFO --- report name was requested, returning: '{self.report_name}'")
    #     return self.report_name
    #
    # def __getReportTournamentIDFilter(self):
    #     if self.verbose: print(f"INFO --- report tournament id filter was requested, returning: '{self.report_tournament_id_filter}'")
    #     return self.report_tournament_id_filter

    #============================================
    # internal functions parsing arguments
    #============================================
    def __handleArgumentsList(self):
        if self.verbose: print(f"INFO --- Full list of arguments: '{self.args_list}'")
        if "--version" in self.args_list:
            self.__helpCheck("--version")
        else:
            args_list_len = len(self.args_list)
            for i in range(args_list_len):
                if self.verbose: print(f"DEBUG --- LOOP: '{i}' --- Parsing launch argument: '{self.args_list[i]}'")
                if self.args_list[i] in ["--help", "-h"] and i == 0:
                    self.__helpCheck(self.args_list[i])
                if i < args_list_len-1:
                    if self.args_list[i+1] in ["--help", "-h"]:
                        self.__helpCheck(self.args_list[i])
                if "=" not in self.args_list[i]:
                    self.used_args_list.append(self.args_list[i])
                    self.used_args_value_dict[self.args_list[i]] = None
                else:
                    arg_elements = self.args_list[i].split("=")
                    self.__assignVariables(arg_elements[0], arg_elements[1])

    def __helpCheck(self, arg):
        self.was_help_requested = True
        if self.verbose: print(f"INFO --- Help asked for argument: '{arg}'")
        try:
            arg_elements = arg.split("=")
            helpSelector(arg_elements[0])
        except:
            helpSelector(arg)

    def __assignVariables(self, key, value): #TODO analyze if this match/case can be removed by some auto populate logic
        match key:
            case "--file" | "-f":
                if self.source_excel != "": raise Exception(f"One file name already provided, only one value for '{key}' is expected")
                self.source_excel = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--sheet" | "-s":
                self.source_excel_sheet_list.append(value)
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = self.source_excel_sheet_list
            case "--db_name":
                if self.database_name != "": raise Exception(f"One file name already provided, only one value for '{key}' is expected")
                self.database_name = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--out" | "-o":
                if self.output_type != "": raise Exception(f"One value for '{key}' is expected")
                self.output_type = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--c_name":
                if self.category_name != "": raise Exception(f"One value for '{key}' is expected")
                self.category_name = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--c_desc":
                if self.category_desc != "": raise Exception(f"One value for '{key}' is expected")
                self.category_desc = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--r_name":
                if self.report_name != "": raise Exception(f"One value for '{key}' is expected")
                self.report_name = value
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = value
            case "--r_tidf":
                if self.report_tournament_id_filter != "": raise Exception(f"One value for '{key}' is expected")
                self.report_tournament_id_filter = str(value)
                self.used_args_list.append(key)
                self.used_args_value_dict[key] = str(value)
            case _:
                if self.verbose: print(f"DEBUG --- key/value handler ended in default state handing key: '{key}' and value: '{value}'")
