from BSC.Utils.commands import Command, Argument

#TODO the info and content of both commands and arguments should be created here outside function with actul useful details
def registerCommands():
    db_name = Argument("SQLite database name", "--db_name", is_mandatory=True)
    excel_file = Argument("Excel source file", "--file", "-f", is_mandatory=True)
    excel_sheet = Argument("Excel sheet", "--sheet", "-s", is_mandatory=True)
    c_name = Argument("category short name", "--c_name", is_mandatory=True)
    c_desc = Argument("category description", "--c_desc", is_mandatory=True)
    output_type = Argument("output format", "--out", "-o")
    verbose = Argument("output verbose information", "--verbose", "-v")
    help_arg = Argument("display help information", "--help", "-h")
    list_options = Argument("lists available options", "--list", "-l")
    report_name = Argument("report name to be ran", "--name", "-n")

    cli_commands_dict = {}
    cli_commands_dict["version"] = Command("version", "shows app version info", test)
    cli_commands_dict["help"] = Command("help", "main help info of the app", commandHelp) #TODO initial help should also be both '-h' and '--help'
    cli_commands_dict["insert"] = Command("insert", "insert new tournament to database", test, db_name, excel_file, excel_sheet, c_name, c_desc, output_type, verbose, help_arg)
    cli_commands_dict["report"] = Command("report", "use reports/views from database", test, db_name, list_options, report_name, help_arg)
    cli_commands_dict["category"] = Command("category", "list or add category", test, db_name, list_options, c_name, c_desc, help_arg)
    return cli_commands_dict

def test():
    print("hello from command")

def commandHelp(commands):
    for k,v in commands.items():
        print(v)
        for arg in v.arguments:
            print(arg)
        print("")
