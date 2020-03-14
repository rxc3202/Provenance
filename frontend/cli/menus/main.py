from frontend.cli.menus.menu import Menu
import os


class WelcomeMenu(Menu):

    def menu_Exec_Shell(self, **kwargs):
        print("Type 'exit' to exit")
        while True:
            cmd = input("$> ")
            if cmd == "exit":
                break
            os.system(f"powershell -command \"{cmd}\"")

    def menu_View_Options(self, **kwargs):
        pass

    def menu_View_Logs(self, **kwargs):
        pass

    def menu_Machines(self, **kwargs):
        self.switch_menu("machine")
