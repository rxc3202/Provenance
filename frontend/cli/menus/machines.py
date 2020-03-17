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
        model = kwargs["model"]
        table = PrettyTable()
        table.field_names = ["#", "UID", "Command"]
        host = ""
        while host not in model.get_hosts():
            host = input("Enter IP: ")
        for i, cmd in enumerate(model.get_queued_commands(host)):
            table.add_row([i, cmd[2], cmd[1]])
        print(table)
        uid = int(input("Enter Command UID: "))
        model.remove_command(host, uid)
        print(f"Command {uid} Deleted!")
        time.sleep(2)

    def menu_View_Commands(self, **kwargs):
        print("[view-commands] <ip>")
        table = PrettyTable()
        table.field_names = ["#", "UID", "Command"]
        model = kwargs["model"]
        host = ""
        while host not in model.get_hosts():
            host = input("[view-commands]> ")
        for i, cmd in enumerate(model.get_queued_commands(host)):
            table.add_row([i, cmd[2], cmd[1]])
        print(table)
        input("Press any key to continue...")

    def menu_Add_Host(self, **kwargs):
        print("[add-host] <ip>")
        host = input("Enter IP to Track: ")
        # TODO: do IP format checking
        res = kwargs["model"].add_host(host)
        if res:
            print(f"Host \"{host}\" Added!")
        else:
            print(f"Error adding host")
        time.sleep(.5)


    def menu_Remove_Host(self, **kwargs):
        pass
