from enum import Enum
import os
import sys


class FGColors(Enum):
    BLACK = '\033[30m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PINK = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


class BGColors(Enum):
    BLACK = '\033[40m'
    RED = '\033[101m'
    GREEN = '\033[102m'
    YELLOW = '\033[103m'
    BLUE = '\033[104m'
    PINK = '\033[105m'
    CYAN = '\033[106m'
    WHITE = '\033[107m'


class Menu(object):

    current_menu = None
    os = sys.platform

    def __init__(self, name, banner):
        self.name = name
        self.banner = banner
        self.parent = None
        self.actions = []

    @classmethod
    def print(cls, string, color, end="\n"):
        if sys.platform == 'win32':
            print(string)
        else:
            print(color.value + string + "\033[0m")

    def up(self):
        self.current_menu = self.parent
        self.current_menu.display_actions()
        self.current_menu.act()

    def print_banner(self):
        Menu.print(self.banner, FGColors.PINK)

    def add_action(self, name, func):
        self.actions.append((name, func))

    def display_actions(self):
        """
        Displays the options in this menu
        :return: None
        """
        Menu.print("Available Actions:", FGColors.WHITE)
        for i, item in enumerate(self.actions):
            Menu.print(f"[{i}] {item[0]}", FGColors.BLUE)

    def act(self):
        """
        The method that runs the main function of this menu
        :return: None
        """
        try:
            choice = int(input(">> "))
            self.actions[choice][1]()
        except ValueError:
            os.system("cls||clear")
            self.print_banner()
            self.display_actions()
            self.act()
        except KeyboardInterrupt:
            sys.exit(0)

