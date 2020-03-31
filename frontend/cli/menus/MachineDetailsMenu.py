from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from controllers.intefaces.model import ModelInterface


class MachineDetailsMenu(Frame):

    reset_data = {"active": "", "ip": "", "hostname": "", "beacon": "", "commands": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height * 2 // 3, width=screen.width * 2 // 3,
                         can_scroll=False, title="View Host", hover_focus=True)

        self._model: ModelInterface = model

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