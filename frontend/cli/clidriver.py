from frontend.cli.menus import *
from frontend.cli.menus.menu import Menu
import os


class CLIDriver(object):

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
    prompt = ">>"

    def __init__(self, init_menu, menus):
        super().__init__()
        self.current_menu = init_menu
        self.menus = menus

    def switch_menu(self, menu):
        self.current_menu = self.menus[menu]

    def print_banner(self):
        os.system("cls||clear")
        print(self.banner)

    def print_header(self):
        self.current_menu.print_header()

    def run(self):
        while True:
            self.print_banner()
            self.print_header()
            self.current_menu.display_actions()
            self.current_menu.act()

    @staticmethod
    def generate():
        main_menu = WelcomeMenu("Main Menu", None, None, None)
        main_menu.generate()
        machine_menu = MachineMenu(name="Machines", header=None, parent="main", actions=None)
        machine_menu.generate()
        menus = {
            "main": main_menu,
            "machine": machine_menu
        }

        cli_driver = CLIDriver(main_menu, menus)
        Menu.context_driver = cli_driver
        return cli_driver


