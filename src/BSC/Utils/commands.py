spacing = "             "
spacing_long = "                        "

commands_info = {
"version": "Shows application version information",
"help": "Initial help information, for more details use [command] --help",
"insert": "Insert new tournament to database",
"report": "Use reporting views from database",
"category": "List or add tournament categories"
}

arguments_info = {
"--db_name": "SQLite database name to be used, will create new one if it does not exist",
"--file": "Input Excel file of tournament results to parsed and injected",
"--sheet": "Excel sheet name to be parsed, multiple sheets can be defined in one execution",
"--c_name": "Short name of the category to be used or inserted to the database",
"--c_desc": "Category description",
"--out": f"""Output format, by default prints human readble results to terminal.
{spacing_long}'-out=json' will output response in json format for when other applications need to parse the results""",
"--verbose": "Enables verbose output, only works if using default output",
"--help": "Provides more details on how to use the command",
"--list": "Lists available options from database",
"--r_name": "Name of the reporting view to be used to get output",
"--r_tidf": "Report Tournament ID filter for some specific reports that can utilize filtering"
}

class Command():
    def __init__(self, name, info, function, *args):
        self.name = name
        self.info = info
        self.run = function
        self.arguments = args

    def __str__(self):
        command_len = len(self.name)
        command_name = f"{spacing[command_len-3:]}[{self.name}]"
        return f"{command_name}  ::  {self.info}"

class Argument():
    def __init__(self, long_name, info, short_name=None, is_mandatory=False, function=None):
        self.info = info
        self.arg_options = [long_name]
        self.is_mandatory = is_mandatory
        self.run = function
        if short_name != None: self.arg_options.append(short_name)

    def __str__(self):
        madatory = ""
        long_name_len = len(self.arg_options[0])
        long_name = spacing[long_name_len:] + self.arg_options[0]
        if self.is_mandatory:
            madatory = " - MANDATORY"
        if len(self.arg_options) != 2:
            short_name = "  "
        else:
            short_name = self.arg_options[1]
        return f"{long_name},  {short_name}  ::  {self.info}{madatory}"
