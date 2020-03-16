import shlex
from frontend.cli.menus.menu import Menu
from prettytable import PrettyTable
import time


class MachineMenu(Menu):

    def print_header(self, **kwargs):
        self._display_hosts(kwargs["model"])

    def _display_hosts(self, model):
        table = PrettyTable()
        table.field_names = ["Hostname", "IP Address", "Last Active", "Queued Commands"]
        for ip in model.get_hosts():
            info = model.get_machine_info(ip)
            table.add_row([f for f in info])
        print(table)

    # Menu Commands
    def menu_Back(self, **kwargs):
        self.switch_menu(self.parent)

    def menu_Queue_Command(self, **kwargs):
        print("[queue-command] <bash|ps|cmd> <ip> \"<cmd>\"")
        args = shlex.split(input("[queue-command]> "))
        kwargs["model"].queue_command(*args)
        print(f"\"{args[3]}\" Added!")
        time.sleep(2)

    def menu_Verify_Command(self, **kwargs):
        print("type 'exit' to exit")
        while True:
            args = shlex.split("testarg1 " + input("[enter-command]> "))
            if args[1] == "exit":
                break
            print("Parsed Command(s): \n")
            for cmd in args[1:]:
                print("\t" + cmd)
            print()

    def menu_Remove_Command(self, **kwargs):
        print("Removing Command ...")

    def menu_View_Commands(self, **kwargs):
        table = PrettyTable()
        table.field_names = ["ID", "Command"]
        host = input("Enter IP: ")
        for i, cmd in enumerate(kwargs["model"].get_queued_commands(host)):
            table.add_row([i, cmd[1]])
        print(table)
        input("Press any key to continue...")
