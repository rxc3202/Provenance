from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, CheckBox, DropdownList
from asciimatics.exceptions import NextScene
import logging
from controllers import *


class SettingsMenu(Frame):

    reset_data = {}

    _logging_options = {
        "Debug": 0,
        "Info": 1,
        "Warning": 2,
        "Error": 3,
        "Critical": 4
    }

    def __init__(self, screen, model, logger):
        super().__init__(screen, height=screen.height // 2, width=screen.width // 2,
                         can_scroll=False, title="Settings", hover_focus=True)
        self._logger: LoggingController = logger
        self._model: ModelController = model
        self.set_theme("default")

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._discovery = CheckBox("All hosts that connect are regarded as clients", label="Discovery", name="discovery")
        self._display_logs = CheckBox("Display logs on the main menu", label="Display Logs", name="logs")
        self._log_level_widget = DropdownList([("Debug", logging.DEBUG),
                                               ("Info", logging.INFO),
                                               ("Warning", logging.WARNING),
                                               ("Error", logging.ERROR),
                                               ("Critical", logging.CRITICAL)],
                                              label="Logging Level: ",
                                              name="loglevel")
        self._refreshrate = Text(label="Refresh Rate (s):", name="refresh")
        # Set default values
        self._refreshrate.value = str(2)
        self._log_level_widget.value = self._logger.log_level

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._discovery)
        layout.add_widget(self._display_logs)
        layout.add_widget(self._log_level_widget)
        layout.add_widget(self._refreshrate)

        button_layout = Layout([1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._confirm_button, 0)
        button_layout.add_widget(self._cancel_button, 1)

        # Save Layouts
        self.fix()

    # Widget Specific Fnctions
    def update_refresh(self):
        """
        Propogate the refresh rate to Main Menu
        :return: None
        """
        pass

    def reset(self):
        super(SettingsMenu, self).reset()
        self.data = self.reset_data

    def _cancel(self):
        self.reset()
        raise NextScene("Main")

    def _confirm(self):
        self.save()
        self._logger.log_level = self.data["loglevel"]
        raise NextScene("Main")
