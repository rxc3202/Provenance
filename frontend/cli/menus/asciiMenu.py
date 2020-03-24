from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
from frontend.util.structs import ClientInfo
import sys

from controllers.modelcontroller import Controller


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
        if not id:
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


class MachineDetailsMenu(Frame):

    reset_data = {"active": "", "ip": "", "hostname": "", "beacon": "", "commands": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height * 2 // 3, width=screen.width * 2 // 3,
                         can_scroll=False, title="View Host", hover_focus=True)

        self._model = model

        # Initialize Widgets
        self._confirm_button = Button("Finish", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._hostname_field = Text("Hostname", name="hostname", disabled=True)
        self._ip_field = Text("IP Address", name="ip", disabled=True)
        self._beacon_field = Text("Beacon Type", name="beacon", disabled=True)
        self._last_active_field = Text("Last Active", name="active", disabled=True)
        self._commands_field = self._init_command_list()

        info_layout = Layout([1], fill_frame=True)
        self.add_layout(info_layout)
        info_layout.add_widget(self._hostname_field)
        info_layout.add_widget(self._ip_field)
        info_layout.add_widget(self._beacon_field)
        info_layout.add_widget(self._last_active_field)
        info_layout.add_widget(self._commands_field)
        info_layout.add_widget(Divider())

        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, column=0)
        button_layout.add_widget(self._cancel_button, column=1)

        # Confirm Frame
        self.fix()

    # Backend Initialization Methods
    def _init_command_list(self):
        fields = []
        if self._model.current_machine:
            commands = self._model.get_queued_commands(self._model.current_machine)
            fields = [(item.command, i) for i, item in enumerate(commands)]
        return ListBox(
            Widget.FILL_FRAME,
            options=fields,
            name="commands",
            label="Queued Commands"
        )

    def reset(self):
        super(MachineDetailsMenu, self).reset()
        current_machine = self._model.current_machine
        if current_machine:
            info = self._model.get_machine_info(current_machine)
            self.data = {
                "beacon": info.beacon,
                "hostname": info.hostname,
                "ip": info.ip,
                "active": info.active,
            }
            self._commands_field.options = [(item.command,i) for i,item in enumerate(info.commands)]
        else:
            self.data = self.reset_data

    def _confirm(self):
        self._model.reset_current()
        raise NextScene("Main")

    def _cancel(self):
        self._model.reset_current()
        raise NextScene("Main")


class AddMachineMenu(Frame):

    reset_data = {"ip": "", "hostname": "", "beacon": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height //2, width=screen.width //2, can_scroll=False, title="Add Host",
                         hover_focus=True)

        self.model = model

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address", name="ip")
        self._hostname_input = Text("Hostname", name="hostname")
        self._beacon_type = DropdownList([("DNS", "DNS"), ("HTTP", "HTTP"), ("ICMP", "ICMP")],
                                         label="Beacon Type", name="beacon")

        self.set_theme("default")

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._hostname_input)
        layout.add_widget(self._ip_input)
        layout.add_widget(self._beacon_type)
        layout.add_widget(TextBox(Widget.FILL_FRAME, disabled=True))
        layout.add_widget(Divider())
        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    def reset(self):
        super(AddMachineMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.save()
        self.model.add_host(self.data["ip"], hostname=self.data["hostname"])
        raise NextScene("Main")


class DeleteMachineMenu(Frame):

    reset_data = {"ip": "", "hostname": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height //5, width=screen.width //2, can_scroll=False, title="Delete Host",
                         hover_focus=True)

        self.model = model

        self.set_theme("default")

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address", name="ip")
        self._or = Text("OR", disabled=True)
        self._hostname_input = Text("Hostname", name="hostname")

        self.set_theme("default")

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._hostname_input)
        layout.add_widget(self._or)
        layout.add_widget(self._ip_input)
        layout.add_widget(TextBox(Widget.FILL_FRAME, disabled=True))
        layout.add_widget(Divider())
        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    def reset(self):
        super(DeleteMachineMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        raise NextScene("Main")


class DeleteCommandsMenu(Frame):

    reset_data = {"ip": "", "hostname": ""}

    def __init__(self, screen):
        super().__init__(screen, height=screen.height // 5, width=screen.width // 2,
                         can_scroll=False, title="Delete Host", hover_focus=True)
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address", name="ip")
        self._hostname_input = Text("Hostname", name="hostname")

        self.set_theme("default")

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._hostname_input)
        layout.add_widget(self._ip_input)
        layout.add_widget(TextBox(Widget.FILL_FRAME, disabled=True))
        layout.add_widget(Divider())
        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    def reset(self):
        super(DeleteCommandsMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.reset()
        raise NextScene("Main")


class ProvenanceCLI(object):

    model = None
    last_scene = None

    @classmethod
    def run(cls):
        def driver(screen, scene):
            scenes = [
                Scene([MainMenu(screen, cls.model)], -1, name="Main"),
                Scene([MainMenu(screen, cls.model), AddMachineMenu(screen, cls.model)], -1, name="Add Host"),
                Scene([MainMenu(screen, cls.model), DeleteMachineMenu(screen, cls.model)], -1, name="Delete Host"),
                Scene([MachineDetailsMenu(screen, cls.model)], -1, name="View Host"),
            ]
            screen.play(scenes, stop_on_resize=False, start_scene=scene)

        while True:
            try:
                Screen.wrapper(driver, catch_interrupt=True, arguments=[cls.last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                cls.last_scene = e.scene
