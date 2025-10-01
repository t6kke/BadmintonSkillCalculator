import json

class Output():
    def __init__(self, output_type):
        self.output_type = output_type
        self.write = None
        self.json_output_result = {}
        self.__determineOutputFunction()

    def PrintResult(self):
        if self.json_output_result != {}:
            print(json.dumps(self.json_output_result))
            #print(json.dumps(self.json_output_result, indent=4))

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
            print(f"{message_type} --- {':'.join(message_key)} --- ", end="")
            for v in key_message.values():
                print(v, end="  ")
            print("")
        else:
            for v in key_message.values():
                print(v,end="  ")
            print("")

    def __toJson(self, verbose, message_type, message_key, **key_message):
        if verbose: pass #json output will not have verbose information
        index = -1
        if message_key == None:
            self.json_output_result.update(key_message) #TODO this will overwrite if key is matching, find a solution
            return
        if ":" in message_key:
            keys = message_key.split(":")
            if self.json_output_result.get(keys[0])[index].get(keys[1]) == None:
                self.json_output_result[keys[0]][index][keys[1]] = []
            self.json_output_result[keys[0]][index][keys[1]].append(key_message)
            #self.__addToKey(self.json_output_result, message_key, key_message)
        else:
            if self.json_output_result.get(message_key) == None:
                self.json_output_result[message_key] = []
            self.json_output_result[message_key].append(key_message)
            index += 1

    #intended for recursive logic to add data to final dictionary, not working and not needed in current situation
    def __addToKey(self, data, target_key, value):
        print(data)
        if isinstance(data, dict):
            for k, v in data.items():
                if k == target_key:
                    data[k].append(value)
                    return True
                if self.__addToKey(v, target_key, value):
                    return True
        elif isinstance(data, list):
            for item in data:
                if self.__addToKey(v, target_key, value):
                    return True

        return False
