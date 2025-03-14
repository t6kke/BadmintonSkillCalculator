from BSC.Utils.handlehelp import helpSelector

class HandleArgs():
    def __init__(self, args_list, verbose=False):
        #argument values variables to be filled
        self.source_excel = ""
        self.source_excel_sheet_list = []

        # general class variables
        self.verbose = verbose
        self.args_list = args_list
        self.was_help_requested = False
        #parse arguments on initilization
        self.__convertListToDict()


    #============================================
    # variable get functions
    #============================================
    def wasHelpRequested(self):
        return self.was_help_requested

    def getSourceExcelFileName(self):
        return self.source_excel

    def getExcelSheetsList(self):
        return self.source_excel_sheet_list

    #============================================
    # internal functions parsing arguments
    #============================================
    def __convertListToDict(self):
        if self.verbose: print(f"INFO --- Full list of arguments: '{self.args_list}'")
        args_list_len = len(self.args_list)
        for i in range(args_list_len):
            if self.verbose: print(f"DEBUG --- LOOP: '{i}' --- Parsing launch argument: '{self.args_list[i]}'")
            if self.args_list[i-1] in ["--help", "-h"] and i == 0:
                self.__helpCheck(self.args_list[i-1])
            if i < args_list_len-1:
                if self.args_list[i+1] in ["--help", "-h"]:
                    self.__helpCheck(self.args_list[i])
            if "=" not in self.args_list[i]:
                pass #TODO handle arguments that don't have key/value pair
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

    def __assignVariables(self, key, value):
        match key:
            case "--file" | "-f":
                if self.source_excel != "":
                    raise Exception(f"One file name already provided, only one value for '{key}' is expected")
                self.source_excel = value
            case "--sheet" | "-s":
                self.source_excel_sheet_list.append(value)
            case _:
                if self.verbose: print(f"DEBUG --- key/value handler ended in default state handing key: '{key}' and value: '{value}'")
