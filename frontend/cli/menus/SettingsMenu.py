from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, CheckBox, DropdownList
from asciimatics.exceptions import NextScene
import logging


class SettingsMenu(Frame):

    reset_data = {}

    def __init__(self, screen, model):
        super().__init__(screen, height=screen.height // 2, width=screen.width // 2,
                         can_scroll=False, title="Settings", hover_focus=True)
        self._model = model
        self.set_theme("default")

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._discovery = CheckBox("All hosts that connect are regarded as clients", label="Discovery", name="discovery")
        self._display_logs = CheckBox("Display logs on the main menu", label="Display Logs", name="logs")
        self._log_level = DropdownList([("Debug", logging.DEBUG),
                                        ("Info", logging.INFO),
                                        ("Warning", logging.WARNING),
                                        ("Error", logging.ERROR),
                                        ("Critical", logging.CRITICAL)],
                                       label="Logging Level: "
                                       )

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._discovery)
        layout.add_widget(self._display_logs)
        layout.add_widget(self._log_level)

        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    def reset(self):
        super(SettingsMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.reset()
        raise NextScene("Main")