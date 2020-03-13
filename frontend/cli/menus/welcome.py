from frontend.cli.menus.menu import Menu
import os


class WelcomeMenu(Menu):

    banner = """
    Welcome to the ...
     ______                                                           
    (_____ \                                                          
     _____) )____  ___  _   _  ____  ____    ____  ____    ____  ____ 
    |  ____// ___)/ _ \| | | |/ _  )|  _ \  / _  ||  _ \  / ___)/ _  )
    | |    | |   | |_| |\ V /( (/ / | | | |( ( | || | | |( (___( (/ / 
    |_|    |_|    \___/  \_/  \____)|_| |_| \_||_||_| |_| \____)\____)
                                    Command and Control Platform
    """

    def _view_machines(self):
        pass

    def _exec_shell(self):
        print("Type 'exit' to exit")
        while True:
            cmd = input("$> ")
            if cmd == "exit":
                break
            os.system(cmd)

    def _view_options(self):
        pass

    @classmethod
    def generate(cls):
        actions = [
            ("View Machines", cls._view_machines),
            ("View Options", cls._view_options),
            ("Shell Execute", cls._exec_shell)
        ]

        main_menu = WelcomeMenu(name="Main Menu", banner=cls.banner, parent=None, actions=actions)
        return main_menu

