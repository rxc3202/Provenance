from frontend.cli.menus.menu import Menu
import time

class MachineMenu(Menu):

    def menu_Back(self):
        self.switch_menu(self.parent)

    def forward(self, menu):
        self.switch_menu(menu)

    def menu_Queue_Command(self, **kwargs):
        print(f"Queueing Command ...{kwargs}")

    def menu_Remove_Command(self, **kwargs):
        print("Removing Command ...")

    def menu_View_Commands(self, **kwargs):
        print("view-command <ip>")
        host = input(">> ")
        print(kwargs["model"].get_queued_commands(host))
        time.sleep(5)
