def helpSelector(key):
    match key:
        case "--help" | "-h":
            __generalAppHelp()
        case "--file" | "-f":
            __fileArgumentHelp()
        case "--sheet" | "-s":
            __sheetArgumentHelp()
        case _:
            print(f"argument key '{key}' not found\n")
            __generalAppHelp()

def __generalAppHelp():
    help_text = """ info about app """
    print(help_text)

def __fileArgumentHelp():
    help_text = """ info about file argument """
    print(help_text)

def __sheetArgumentHelp():
    help_text = """ info about sheet argument """
    print(help_text)
