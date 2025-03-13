class HandleArgs():
    def __init__(self, args_list, verbose=False):
        self.args_list = args_list
        self.__convertListToDict()
        #TODO create object variables, each launch argument should be handled as object argument

    def __convertListToDict(self):
        for arg in self.args_list:
            pass #TODO parse launch arguments and assign object variable values
