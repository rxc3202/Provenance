from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from controllers.intefaces.model import ModelInterface
from ipaddress import IPv4Address


class AddMachineMenu(Frame):

    reset_data = {"ip": "", "hostname": "", "beacon": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height //2, width=screen.width //2, can_scroll=False, title="Add Host",
                         hover_focus=True)

        self._model: ModelInterface = model

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address: ", name="ip")
        self._hostname_input = Text("Hostname (optional):", name="hostname")
        self._beacon_type = DropdownList([("DNS", "DNS"), ("HTTP", "HTTP"), ("ICMP", "ICMP")],
                                         label="Beacon Type: ", name="beacon")

        self.set_theme("default")

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._ip_input)
        layout.add_widget(self._hostname_input)
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

    def _validate(self):
        def fail(msg):
            dialog = PopUpDialog(self._screen, f"  {msg}  ", buttons=["OK"], theme="warning")
            self._scene.add_effect(dialog)
            return False

        if not self.data["ip"]:
            return fail("Please enter an IP address.")
        else:
            try:
                IPv4Address(self.data["ip"])
            except ValueError:
                return fail(f"{self.data['ip']} is not a valid IPv4 address")

        if not self.data["beacon"]:
            fail("Please select the beacon of this host.")

    def _confirm(self):
        self.save()
        if not self._validate():
            return

        self._model.add_host(self.data["ip"], hostname=self.data["hostname"])
        raise NextScene("Main")
