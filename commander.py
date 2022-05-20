class Commander:
    def __init__(self,):
        self.com_symbol = '$'
        self.CMD_send = 'send'
        self.CMD_exit = 'exit'
        self.CMD_switch = '!'
        self.CMD_subscribed = '?'
        self.CMD_help = '$'

        self.non_arg_cmd_lst = [self.CMD_exit, self.CMD_help, self.CMD_subscribed]

    def set_actions(self, commands: dict):
        self.commands = commands

    def help(self):
        print(f"""help  text\nCommand sybol is {self.com_symbol}.\nTo send message: type text and hit Enter.
To switch channel type: {self.com_symbol}{self.CMD_switch}<space><channel_name> and hit Enter.
Type {self.com_symbol}{self.CMD_exit} to exit the chat.
Type {self.com_symbol}{self.CMD_subscribed} to see channels you are already subscribed to.
Type {self.com_symbol}{self.CMD_help} to see help text.
______________________________________________________""")

    def exit_cmdr(self):
        print("End of session")

    def parse_execute(self, str_in: str):
        if len(str_in) == 0:
            return

        if str_in[0] == self.com_symbol:

            # No args commands
            for cmd in self.non_arg_cmd_lst:
                if str_in[1:] == cmd:
                    self.commands[cmd]()
                    return

            command_only = str_in[1:].split(' ')[0]

            # One arg commands
            if command_only == self.CMD_switch:
                self.commands[self.CMD_switch](str_in.split(' ')[1])
                return

        else:
            self.commands[self.CMD_send](str_in)
            return

    def input_loop(self):
        exit_str = self.com_symbol + self.CMD_exit

        str_in = ""

        while (str_in != exit_str):
            str_in = input("")
            self.parse_execute(str_in)
