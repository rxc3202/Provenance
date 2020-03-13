from frontend.cli.menus.menu import Menu


class MachineMenu(Menu):

    def menu_Back(self):
        self.switch_menu(self.parent)

    def forward(self, menu):
        self.switch_menu(menu)

    def menu_Queue_Command(self):
        print("Queueing Command ...")

    def menu_Remove_Command(self):
        print("Removing Command ...")

    def menu_View_Commands(self):
        print("Viewing Commands ...")

