from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import sys

from controllers.modelcontroller import Controller


class MainMenu(Frame):

    test_machines = [("DNS", "Host1", "127.0.0.1", "0m", "whoami"),
                     ("DNS", "Host2", "127.0.0.2", "5m", "python -c \"import sys; sys.exec(\"/bin/bash\")"),
                     ("DNS", "Host3", "127.0.0.3", "0m", "ls"),
                     ("DNS", "Host4", "127.0.0.4", "0m", "cd C:\\"),
                     ]

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
        self._exit_button = Button("Exit", self._exit_command)
        self._add_host_menu = PopUpDialog(screen, "Add Host", buttons=[])

        # Generation
        upper_half = Layout([1], fill_frame=True)
        self.add_layout(upper_half)
        upper_half.add_widget(self._machine_list_widget)
        upper_half.add_widget(Divider())

        # upper_half.add_widget(self._add_host_menu)

        actions_list = Layout([1, 1, 1, 1, 1])
        self.add_layout(actions_list)
        actions_list.add_widget(self._add_host_button, 0)
        actions_list.add_widget(self._rem_host_button, 1)
        actions_list.add_widget(self._add_cmd_button, 2)
        actions_list.add_widget(self._rem_cmd_button, 3)
        actions_list.add_widget(self._exit_button, 4)

        # Confirm Frame
        self.fix()

    # Widget Initializations

    def _init_filter_widget(self):
        pass

    def _init_machine_list_widget(self):
        machines = self._refresh_hosts()

        fields = ["Type", "Hostname", "IP", "Last Active", "Next Command"]
        #alignment = ["<5", "<15", "<12", "<5", "^0"]
        return MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[f"<{100//len(fields)}%" for _ in fields],
            #columns=alignment,
            options=[(x, i) for i, x in enumerate(machines)],
            titles=fields,
            add_scroll_bar=True,
            #on_select=self._select_machine
        )

    # Backend Methods
    def _refresh_hosts(self):
        machines = []
        for ip in self.model.get_hosts():
            info = self.model.get_machine_info(ip)
            next_command = info.cmd[0].command if info.cmd else "N/A"
            tup = (info.beacon, info.hostname, info.ip, info.active, next_command)
            machines.append(tup)
        return machines

    def _reload_page(self):
        machines = self._refresh_hosts()
        self._machine_list_widget.options = [(x, i) for i, x in enumerate(machines)]

    # Menu Actions Methods
    def _add_host(self):
        raise NextScene("Add Host")

    def _remove_host(self):
        raise NextScene("Delete Host")

    def _add_command(self):
        pass

    def _remove_command(self):
        pass

    def _exit_command(self):
        sys.exit(0)


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

        self.set_theme("green")

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
        self.reset()
        raise NextScene("Main")


class DeleteMachineMenu(Frame):

    reset_data = {"ip": "", "hostname": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height //5, width=screen.width //2, can_scroll=False, title="Delete Host",
                         hover_focus=True)

        self.model = model

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address", name="ip")
        self._hostname_input = Text("Hostname", name="hostname")

        self.set_theme("green")

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
        super(DeleteMachineMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.reset()
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

        self.set_theme("green")

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
            ]
            screen.play(scenes, stop_on_resize=False, start_scene=scene)

        while True:
            try:
                Screen.wrapper(driver, catch_interrupt=True, arguments=[cls.last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                cls.last_scene = e.scene


if __name__ == '__main__':
    def run(screen, scene):
        scenes = [
            Scene([MainMenu(screen, None)], -1, name="Main"),
            Scene([MainMenu(screen, None), AddMachineMenu(screen, None)], -1, name="Add Host"),
            Scene([MainMenu(screen, None), DeleteMachineMenu(screen, None)], -1, name="Delete Host"),
        ]
        screen.play(scenes, stop_on_resize=False, start_scene=scene)


    last_scene = None
    while True:
        try:
            Screen.wrapper(run, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene

