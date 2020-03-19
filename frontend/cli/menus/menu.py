from abc import ABC
from colorama import Fore, init
import os
import sys


class Menu(ABC):

    model = None
    context_driver = None
    action_delimiter = "menu_"

    def __init__(self, name, header, parent, prompt=">>"):
        self.name = name
        self.prompt = prompt
        self.header = header
        self.parent = parent
        funcs = []
        for name in dir(self.__class__):
            if name.startswith(self.action_delimiter):
                funcs.append(name)
        actions = [(f[len(self.action_delimiter):].replace("_", " "), getattr(self, f)) for f in funcs]
        self.actions = actions
        init()  # init colorarma

    def print_header(self, **kwargs):
        self.print(f"{self.name}\n{'=' * len(self.name)}", Fore.WHITE)

    def switch_menu(self, menu):
        self.context_driver.switch_menu(menu)

    def display_actions(self):
        """
        Displays the options in this menu
        :return: None
        """
        for i, item in enumerate(self.actions):
            self.print(f"[{i}] {item[0]}", Fore.WHITE)
        print()

    def act(self):
        """
        The method that runs the main function of this menu
        :return: None
        """
        try:
            choice = int(input(self.prompt))
            self.actions[choice][1]()
        except (ValueError, IndexError):
            pass
        except (KeyboardInterrupt, EOFError):
            pass

    @staticmethod
    def print(string, color, end="\n"):
        print(f"{color}{string}{Fore.RESET}", end=end)

    @staticmethod
    def clear_screen(self):
        os.system("cls||clear")


