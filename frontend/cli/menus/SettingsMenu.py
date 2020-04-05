from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, CheckBox, DropdownList, THEMES as asciimatics_themes
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

    def __init__(self, screen, model: ModelController, logger: LoggingController, ui: UIController):
        super().__init__(screen, height=screen.height // 2, width=screen.width // 2,
                         can_scroll=False, title="Settings", hover_focus=True)

        # Controllers that access different aspects of provenance
        self._logger: LoggingController = logger
        self._model: ModelController = model
        self._ui: UIController = ui
        self._theme = None
        self.set_theme(ui.theme)

        # Initialize Widgets
        self._confirm_button = Button("Confirm", self._confirm)
        self._cancel_button = Button("Cancel", self._cancel)
        self._discovery = CheckBox("All hosts that connect are regarded as clients",
                                   label="Discovery: ",
                                   name="discovery")
        self._display_logs = CheckBox("Display logs on the main menu",
                                      label="Display Logs: ",
                                      name="logs")
        self._log_level_widget = DropdownList([("Debug", logging.DEBUG),
                                               ("Info", logging.INFO),
                                               ("Warning", logging.WARNING),
                                               ("Error", logging.ERROR),
                                               ("Critical", logging.CRITICAL)],
                                              label="Logging Level: ",
                                              name="loglevel")
        self._theme_widget = DropdownList([(t, t) for t in asciimatics_themes.keys()],
                                          label="Theme: ",
                                          name="theme")
        self._refreshrate = Text(label="Refresh Rate (s):", name="refresh")
        # Set default values
        self._refreshrate.value = str(2)
        self._log_level_widget.value = self._logger.log_level
        self._discovery.value = True
        self._display_logs.value = True
        self._theme_widget.value = ui.theme

        # Create and Generate Layouts
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._discovery)
        layout.add_widget(self._display_logs)
        layout.add_widget(self._refreshrate)
        layout.add_widget(self._log_level_widget)
        layout.add_widget(self._theme_widget)

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
        self._ui.theme = self.data["theme"]
        self._ui.refresh_rate = int(self.data["refresh"])
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
