general_help_text = """Usage: python main.py [OPTION] [OPTION] ...

  -h, --help            shows help information of the application
                        or more details of specific arguments

      --version         prints version info about the application

      --verbose         enables verbose information from the code,
                        prints out a lot of information during execution

      --db_name         defines the SQLite database used for storage

      --c_name          Acronym of the category, eg. MD

      --c_desc          Description of the category, eg. "mens double"
                        Must be between quotes for it to be handled as single value

  -f, --file            define the excel file for the scope of
                        the scan, only one is allowed

  -s, --sheet           define the sheet to be scanned from the
                        previously defined excel file, multiple -s
                        arguments can be used

Examples:
  python main.py --db_name=file.db -f=file.xlsx -s=Sheet1 --verbose --c_name=EC --c_desc="example"      file.xlsx and Sheet1 is attempted to be scanned
                                                                                                        for results and results calculated while the whole
                                                                                                        workflow is printing out what it's doing

  python main.py --db_name=file.db -f=file.xlsx -s=Sheet1 -s=Sheet2 --c_name=EC --c_desc="example"      file.xlsx and Sheet1, Sheet2 are attempted
                                                                                                        to be scanned for results and results calculated

  pytion main.py -f -h                                                                                  shows specific help information about -f argument

  python main.py                                                                                        just runs example execution of the code with example
                                                                                                        data from .txt file.

GIT repo: https://github.com/t6kke/BadmintonSkillCalculator
"""
version_help_text = """Badminton Skill Calculator
version: Prototype v2
"""
verbose_help_text = """Enables verbose output of the application.

Various functions have loads of print functions that
detail what is going on in the code and what is the
status of the various state of variables in the code.

Information on the verbose info

  INFO      More general information from the code.

  DEBUG     A bit more specific and nuanced information
            compared to the INFO logs.

  LOOP      Verbose info within loops have this entry
            and mark on what index of the loop the code
            is at.
"""
file_argument_info_text = """Use case:
-f=[XLSX_FILE]

Only one file can be enterd

Code handels very specific structure based on specific
tournament type that hanles results in that given excel.
"""
sheet_argument_info_text = """Use case:
-s=[SHEET_NAME]

Argument can be used multiple times.
Example:
-s=[SHEET_1] -s=[SHEET_2] -s=[SHEET_3]
"""

db_argument_info_text = """Use case:
--db_name=[DB_NAME]

SQLite is used for database and new one is created if one is not found.
Name should include the '.db' file name extension.

Example:
--db_name=example_database.db
"""

category_argument_info_text = """Use case:
--c_name=[acronym of the category] --c_desc=[long description of the category]

This has to be a unique value, if it exists in database it's used and no new entry is added.
Uniqness is based on the name acronym.
Descriptions has be between quotation marks for it to register as one value.

Example:
--c_name=XD --c_desc="mixed doubles"
--c_name=WD --c_desc="women singles"
"""

def helpSelector(key):
    match key:
        case "--help" | "-h":
            __generalAppHelp()
        case "--version":
            __versionArgInfo()
        case "--verbose":
            __verboseArgInfo()
        case "--file" | "-f":
            __fileArgumentInfo()
        case "--sheet" | "-s":
            __sheetArgumentInfo()
        case "--db_name":
            __dbArgumentInfo()
        case "--c_name":
            __categoryArgumentInfo()
        case "--c_desc":
            __categoryArgumentInfo()
        case _:
            print(f"argument key '{key}' not found\n")
            __generalAppHelp()

def __generalAppHelp():
    print(general_help_text)

def __versionArgInfo():
    print(version_help_text)

def __verboseArgInfo():
    print(verbose_help_text)

def __fileArgumentInfo():
    print(file_argument_info_text)

def __sheetArgumentInfo():
    print(sheet_argument_info_text)

def __dbArgumentInfo():
    print(db_argument_info_text)

def __categoryArgumentInfo():
    print(category_argument_info_text)
