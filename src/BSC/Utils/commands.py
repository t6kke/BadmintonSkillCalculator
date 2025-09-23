class Command():
    def __init__(self, name, info, function, *args):
        self.name = name
        self.info = info
        self.run = function
        self.arguments = args

def Commands():
    cli_commands_dict = {}
    cli_commands_dict["version"] = Command("version", "shows app version info", test)
    cli_commands_dict["help"] = Command("help", "main help info of the app", test)
    cli_commands_dict["insert"] = Command("insert", "insert new tournament to database", test, "--db_name", "-f", "-file", "-s", "--sheet", "--c_name", "--c_desc", "-o", "--out" "-v", "--verbose", "-h", "--help")
    cli_commands_dict["report"] = Command("report", "use reports/views from database", test, "-l", "--list", "-n", "--name", "-h", "--help")
    cli_commands_dict["category"] = Command("category", "list or add category", test, "-l", "--list", "--c_name", "--c_desc", "-h", "--help")
    return cli_commands_dict

def test():
    print("hello from command")
