from asciimatics.widgets import Frame, Layout, Divider, Text, \
    Button, TextBox, Widget, RadioButtons, PopUpDialog
from asciimatics.exceptions import NextScene
from ipaddress import IPv4Network, IPv4Address
from controllers.intefaces.model import ModelInterface
from controllers import UIController


class AddCommandMenu(Frame):
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
        self._ip_input = Text("IPs and/or subnet(s): ", name="ips")
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
        super(AddCommandMenu, self).reset()
        self.data = self.reset_data
        # ascimatics can be poop sometimes
        self.data["commands"].clear()
        self.data["commands"].append('')

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _validate(self):
        def fail(msg):
            dialog = PopUpDialog(self._screen, f"  {msg}  ", buttons=["OK"], theme="warning")
            self._scene.add_effect(dialog)
            return False

        if not self.data["ips"]:
            return fail("Please specify a list of IPs or Subnets to target.")
        else:
            data = self.data["ips"].replace(' ', '').split(",")
            failure = None
            try:
                input_ips = set(filter(lambda x: "/" not in x, data))
                for target in input_ips:
                    failure = target
                    IPv4Address(target)
            except ValueError:
                return fail(f"{failure} is not a valid IPv4 address.")

            try:
                input_subnets = filter(lambda x: "/" in x, data)
                for target in input_subnets:
                    failure = target
                    IPv4Network(target)
            except ValueError:
                return fail(f"{failure} is not valid CIDR subnet notation.")

        # check if there is at least one command entered
        if self.data["commands"].count('') == len(self.data["commands"]):
            return fail("Please enter a command to queue.")

        return True

    def _confirm(self):
        self.save()
        if not self._validate():
            return

        if self.data["ips"]:
            # Get the IPs of the currently tracked hosts
            data = self.data["ips"].replace(' ', '').split(",")
            tracked_ips = set(self._model.get_hosts())
            # Get the IPs of the hosts to issue the command to
            input_ips = set(filter(lambda x: "/" not in x, data))
            input_subnets = set(map(lambda s: IPv4Network(s), filter(lambda x: "/" in x, data)))
            # Get only the IPs of the hosts we're tracking that the user wants to send commands to
            valid_ips = tracked_ips.intersection(input_ips)
            for subnet in input_subnets:
                subnet_ips = set([str(h) for h in subnet.hosts()])
                valid_ips.union(subnet_ips.intersection(tracked_ips))
            for ip in valid_ips:
                for command in self.data["commands"]:
                    # check for empty string
                    if command:
                        self._model.queue_command(self.data["cmdtype"], ip, command)
        elif self.data["hostnames"]:
            pass
        else:
            pass

        raise NextScene("Main")

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
