import json

class Output():
    def __init__(self, output_type):
        self.output_type = output_type
        self.write = None
        self.json_output_result = {}
        self.__determineOutputFunction()

    def PrintResult(self):
        print(json.dumps(self.json_output_result))

    def __determineOutputFunction(self):
        match self.output_type:
            case "json":
                self.write = self.__toJson
            case "log":
                #TODO potentially do also log output in the future
                pass
            case _:
                self.write = self.__consolePrint

    def __consolePrint(self, verbose, message_type, message_key, **key_message):
        if verbose:
            print(f"{message_type} --- {message_key} --- ", end="")
            print(key_message.values())
        else:
            print(key_message.values())

    def __toJson(self, verbose, message_type, message_key, **key_message):
        if verbose: pass #json output will not have verbose information
        data_to_enter = {}
        if len(message_key) == 0:
            return
        if ":" in message_key:
            message_key = message_key.split(":")
        current_key = message_key.pop(0)
        if type(self.json_output_result.get(current_key)) != list:
            self.json_output_result[current_key] = []
        self.json_output_result[current_key].append(key_message)
