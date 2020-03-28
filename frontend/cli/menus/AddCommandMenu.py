from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from ipaddress import IPv4Network, IPv4Address
from controllers.intefaces.model import ModelInterface


class AddCommandMenu(Frame):

    reset_data = {}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height // 2, width=screen.width // 2,
                         can_scroll=False, title="Add Command", hover_focus=True)

        self._model: ModelInterface = model

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IPs and/or subnet(s):", name="ips")
        # self._or = Text("OR", disabled=True)
        # self._hostname_input = Text("Hostname(s):", name="hostnames")
        self._command_input = TextBox(Widget.FILL_FRAME,
                                      label="Command(s):",
                                      name="commands",
                                      line_wrap=True)


        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._ip_input)
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
        super(AddCommandMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.save()
        if not self.data["commands"]:
            pass

        if self.data["ips"]:
            # Get the IPs of the currently tracked hosts
            data = self.data["ips"].split(",")
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
                # TODO: somehow implement choosing command type elegantly
                for command in self.data["commands"]:
                    # check for empty string
                    if command:
                        self._model.queue_command("ps", ip, command)
            raise NextScene("Main")
        elif self.data["hostnames"]:
            pass
        else:
            pass
