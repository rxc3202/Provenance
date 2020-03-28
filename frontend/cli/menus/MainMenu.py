from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from frontend.util.structs import ClientInfo
import sys


class MainMenu(Frame):

    def __init__(self, screen, model):
        super(MainMenu, self).__init__(screen, screen.height,
                                       screen.width, hover_focus=True,
                                       can_scroll=True, on_load=self._reload_page,
                                       title="Main Menu")

        self.model = model

        # Init all widgets
        self._machine_list_widget = self._init_machine_list_widget()
        self._add_host_button = Button("Add Host", self._add_host)
        self._rem_host_button = Button("Remove Host", self._remove_host)
        self._add_cmd_button = Button("Add CMD", self._add_command)
        self._rem_cmd_button = Button("Remove CMD", self._remove_command)
        self._refresh_button = Button("Refresh", self._reload_page)
        self._exit_button = Button("Exit", self._exit_command)

        # Generation
        upper_half = Layout([1], fill_frame=True)
        self.add_layout(upper_half)
        upper_half.add_widget(self._machine_list_widget)
        upper_half.add_widget(Divider())

        actions_list = Layout([1, 1, 1, 1, 1, 1])
        self.add_layout(actions_list)
        actions_list.add_widget(self._refresh_button, 0)
        actions_list.add_widget(self._add_host_button, 1)
        actions_list.add_widget(self._rem_host_button, 2)
        actions_list.add_widget(self._add_cmd_button, 3)
        actions_list.add_widget(self._rem_cmd_button, 4)
        actions_list.add_widget(self._exit_button, 5)

        self.info_layout = upper_half
        self.action_layout = actions_list
        # Confirm Frame
        self.fix()

    # Widget Initializations

    def _init_filter_widget(self):
        pass

    def _init_machine_list_widget(self):
        machines = self._refresh_hosts()

        fields = ["Type", "Hostname", "IP", "Last Active", "Next Command"]
        return MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[f"<{100//len(fields)}%" for _ in fields],
            options=[(x, i) for i, x in enumerate(machines)],
            titles=fields,
            add_scroll_bar=True,
            on_select=self._view_host,
            name="machines"
        )

    # Backend Methods
    def _refresh_hosts(self):
        machines = []
        for ip in self.model.get_hosts():
            info = self.model.get_machine_info(ip)
            next_command = info.commands[0].command if info.commands else "N/A"
            tup = (info.beacon, info.hostname, info.ip, info.active, next_command)
            machines.append(tup)
        return machines

    def _reload_page(self):
        machines = self._refresh_hosts()
        self._machine_list_widget.options = [(x, i) for i, x in enumerate(machines)]

    # Menu Actions Methods
    def _view_host(self):
        self.save()
        # This saves the row that was clicked
        id = self.data["machines"]
        if id is None:
            # TODO: some weird error if entering when all fields are none
            return
        # Get the widget managed by asciimatics
        widget = self.info_layout.find_widget("machines")
        # Get the option displayed on the menu in the MutliColumnListBox
        options = widget.options[id]
        # Unpack the data into a more usable struct
        machine = ClientInfo(*options[0])
        # Select the machine
        self.model.select_current(machine.ip)
        raise NextScene("View Host")

    def _add_host(self):
        raise NextScene("Add Host")

    def _remove_host(self):
        raise NextScene("Delete Host")

    def _add_command(self):
        pass

    def _remove_command(self):
        pass

    def _exit_command(self):
        self.model.shutdown()
        sys.exit(0)
