class Output():
    def __init__(self, output_type):
        self.verbose = verbose
        self.output_type = output_type
        self.write = None
        self.__determineOutputFunction()

    def __determineOutputFunction(self):
        match self.output_type:
            case "json":
                self.write = self.__toJson
            case "log":
                #TODO potentially do also log output in the future
                pass
            case _:
                self.write = self.__consolePrint

    def __consolePrint(self, verbose, message_type, message_key, message_value):
        if verbose:
            print(f"{message_type} --- {message_key} --- ", end="")
            print("message_value")
        else:
            print("message_value")

    def __toJson(self, verbose, message_type, message_key, message_value):
        output_result = {}
        if verbose: pass #json output will not have verbose information
        #TODO building json content to output_result dictionary for json output
        print(output_result)
