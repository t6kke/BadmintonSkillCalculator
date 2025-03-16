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
        case _:
            print(f"argument key '{key}' not found\n")
            __generalAppHelp()

def __generalAppHelp():
    help_text = """Usage: python main.py [OPTION] [OPTION] ...

  -h, --help            shows help information of the application or more details of specific arguments
      --version         number nonempty output lines, overrides -n
      --verbose         enables verbose information from the code, prints out a lot of information during execution
  -f, --file            define the excel file for the scope of the scan, only one is allowed
  -s, --sheet           define the sheet to be scanned from the previously defined excel file, multiple -s arguments can be used

Examples:
  python main.py -f=file.xlsx -s=Sheet1 --verbose                   file.xlsx and Sheet1 is attempted to be scanned for results and results calculated while the whole code is printing out what it's doing
  python main.py -f=file.xlsx -s=Sheet1 -s=Sheet2 -s=Sheet3         file.xlsx and Sheet1, Sheet2, Sheet3 are attempted to be scanned for results and results calculated
  pytion main.py -f -h                                              shows specific help information about -f argument
  python main.py                                                    just runs example execution of the code with example data from .txt file.

GIT repo: https://github.com/t6kke/BadmintonSkillCalculator"""
    print(help_text)

def __versionArgInfo():
    help_text = """Badminton Skill Calculator
version: Prototype v2\n"""
    print(help_text)

def __verboseArgInfo():
    help_text = """ info about verbose argument """
    print(help_text)

def __fileArgumentInfo():
    help_text = """ info about file argument """
    print(help_text)

def __sheetArgumentInfo():
    help_text = """ info about sheet argument """
    print(help_text)
