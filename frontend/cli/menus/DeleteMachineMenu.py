from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene


class DeleteMachineMenu(Frame):

    reset_data = {"ip": "", "hostname": ""}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height // 5, width=screen.width // 2,
                         can_scroll=False, title="Delete Host", hover_focus=True)

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
        self.save()
        if self.data["ip"] or self.data["hostname"]:
            raise NextScene("Main")
        else:
            pass
