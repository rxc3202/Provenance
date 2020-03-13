from abc import ABC, abstractmethod
from colorama import Fore, init
from enum import Enum
import os
import sys


class Menu(ABC):

    current_menu = None
    os = sys.platform

    def __init__(self, name, banner, parent, actions):
        self.name = name
        self.banner = banner
        self.parent = parent
        self.actions = actions
        init() # init colorma


    @classmethod
    def print(cls, string, color, end="\n"):
        print(f"{color}{string}{Fore.RESET}", end=end)

    def up(self):
        self.current_menu = self.parent
        self.current_menu.display_actions()
        self.current_menu.act()

    def print_banner(self):
        Menu.print(self.banner, Fore.WHITE)

    def display_actions(self):
        """
        Displays the options in this menu
        :return: None
        """
        Menu.print("Available Actions:", Fore.WHITE)
        for i, item in enumerate(self.actions):
            Menu.print(f"[{i}] {item[0]}", Fore.WHITE)

    def act(self):
        """
        The method that runs the main function of this menu
        :return: None
        """
        try:
            choice = int(input(">> "))
            self.actions[choice][1](self)
        except (ValueError, IndexError):
            os.system("cls||clear")
            self.print_banner()
            self.display_actions()
            self.act()
        except (KeyboardInterrupt, EOFError):
            os.system("cls||clear")
            sys.exit(0)

