spacing = "             "

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
    def __init__(self, info, long_name, short_name=None, is_mandatory=False):
        self.info = info
        self.arg_options = [long_name]
        self.is_mandatory = is_mandatory
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
