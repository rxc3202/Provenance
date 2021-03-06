from asciimatics.widgets import Frame, Layout, Divider, Text,  Button, TextBox, Widget
from asciimatics.exceptions import NextScene
from controllers.intefaces.model import ModelInterface
from controllers import *


class DeleteMachineMenu(Frame):
    reset_data = {"ip": "", "hostname": ""}

    def __init__(self, screen, model, ui: UIController):
        super().__init__(screen, height=screen.height // 5, width=screen.width // 2,
                         can_scroll=False, title="Delete Host", hover_focus=True)

        self.model: ModelInterface = model
        self._ui: UIController = ui
        self._theme = None
        self.set_theme(ui.theme)

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._ip_input = Text("IP Address", name="ip")
        self._or = Text("OR", disabled=True)
        self._hostname_input = Text("Hostname", name="hostname")

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
