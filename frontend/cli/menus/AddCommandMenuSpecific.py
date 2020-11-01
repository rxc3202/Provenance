from asciimatics.widgets import Frame, Layout, Divider, Text, \
    Button, TextBox, Widget, RadioButtons, PopUpDialog
from asciimatics.exceptions import NextScene
from ipaddress import IPv4Network, IPv4Address
from controllers.intefaces.model import ModelInterface
from controllers import UIController


class AddCommandMenuSpecific(Frame):
    reset_data = {"ips": '', "cmdtype": "ps", "commands": ['']}

    def __init__(self, screen, model, ui: UIController):
        super().__init__(screen, height=screen.height // 2, width=screen.width // 2,
                         can_scroll=False, title="Add Command", hover_focus=True)

        self._model: ModelInterface = model
        self._ui: UIController = ui
        self._theme = None
        self.set_theme(ui.theme)

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IPs and/or subnet(s): ", name="ips", disabled=True)
        self._ip_input.value = self._model.current_machine
        self._command_type = RadioButtons([("Powershell", "ps"), ("DOS", "cmd"), ("Bash", "bash")],
                                          name="cmdtype",
                                          label="Command Type: ")
        # self._or = Text("OR", disabled=True)
        # self._hostname_input = Text("Hostname(s):", name="hostnames")
        self._command_input = TextBox(Widget.FILL_FRAME,
                                      label="Command(s): \n(one per line)",
                                      name="commands",
                                      line_wrap=True)

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._ip_input)
        layout.add_widget(self._command_type)
        # layout.add_widget(self._or)
        # layout.add_widget(self._hostname_input)
        layout.add_widget(Divider())
        layout.add_widget(self._command_input)
        layout.add_widget(Divider())

        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    def reset(self):
        self.save()
        #super(AddCommandMenuSpecific, self).reset()
        self.data = self.reset_data
        # ascimatics can be poop sometimes
        self.data["commands"].clear()
        self.data["commands"].append('')

    def _cancel(self):
        #self.reset()
        raise NextScene("View Host")

    def _validate(self):
        return True

    def _confirm(self):
        self.save()
        if not self._validate():
            return
        uuid = self._model.current_machine
        for command in self.data["commands"]:
            # check for empty string
            if command:
                self._model.queue_command(self.data["cmdtype"], uuid, command)
        raise NextScene("View Host")

    # ====================================
    # Overridden functions
    # ====================================

    def _update(self, frame_no):
        if self._ui.theme != self._theme:
            self.set_theme(self._ui.theme)
        super()._update(frame_no)

    def set_theme(self, theme):
        super().set_theme(theme)
        self._theme = theme
