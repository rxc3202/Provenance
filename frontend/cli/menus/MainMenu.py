from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopupMenu, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from frontend.util.structs import ClientInfo
from controllers import *
import sys


class MainMenu(Frame):

    def __init__(self, screen, model: ModelController, ui: UIController):
        super(MainMenu, self).__init__(screen, screen.height * 3 // 4,
                                       screen.width, hover_focus=True,
                                       can_scroll=False, on_load=self._reload_page,
                                       title="Main Menu", y=0)
        self.model: ModelController = model
        self._ui: UIController = ui
        self._screen = screen
        self._last_frame = 0
        self._refresh_rate = 2
        self._theme = None
        self.set_theme(ui.theme)

        # Init all widgets
        self._machine_list_widget = self._init_machine_list_widget()
        self._add_host_button = Button("Add Host", self._add_host)
        self._rem_host_button = Button("Remove Host", self._remove_host)
        self._add_cmd_button = Button("Add CMD", self._add_command)
        self._rem_cmd_button = Button("Settings", self._options_command)
        self._refresh_button = Button("Refresh", self._refresh)
        self._exit_button = Button("Exit", self._exit_command)

        # Generation
        details_layout = Layout([1], fill_frame=True)
        self.add_layout(details_layout)
        details_layout.add_widget(self._machine_list_widget)
        details_layout.add_widget(Divider())

        button_layout = Layout([1, 1, 1, 1, 1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._refresh_button, 0)
        button_layout.add_widget(self._add_host_button, 1)
        button_layout.add_widget(self._rem_host_button, 2)
        button_layout.add_widget(self._add_cmd_button, 3)
        button_layout.add_widget(self._rem_cmd_button, 4)
        button_layout.add_widget(self._exit_button, 5)

        self._details_layout = details_layout
        self._button_layout = button_layout
        # Confirm Frame
        self.fix()

    # Widget Initializations

    def _init_filter_widget(self):
        pass

    def _init_machine_list_widget(self):
        machines = self._refresh_hosts()

        fields = ["Type", "Hostname", "IP", "Last Active", "Next Command"]
        return MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=[f"<{100//len(fields)}%" for _ in fields],
            options=[(x, i) for i, x in enumerate(machines)],
            titles=fields,
            add_scroll_bar=True,
            on_select=self._view_host,
            name="machines",
        )

    # Backend Methods
    def _refresh_hosts(self):
        machines = []
        for ip in self.model.get_hosts():
            info = self.model.get_machine_info(ip)
            next_command = info.commands[0].command if info.commands else "N/A"
            tup = (info.beacon, info.hostname, info.ip, info.active, next_command)
            machines.append(tup)
        return machines

    def _reload_page(self):
        machines = self._refresh_hosts()
        self._machine_list_widget.options = [(x, i) for i, x in enumerate(machines)]

    # Menu Actions Methods
    def _refresh(self):
        pass

    def _view_host(self):
        self.save()
        # This saves the row that was clicked
        id = self.data["machines"]
        if id is None:
            # TODO: some weird error if entering when all fields are none
            return
        # Get the widget managed by asciimatics
        widget = self._details_layout.find_widget("machines")
        # Get the option displayed on the menu in the MutliColumnListBox
        options = widget.options[id]
        # Unpack the data into a more usable struct
        machine = ClientInfo(*options[0])
        # Select the machine
        self.model.select_current(machine.ip)
        raise NextScene("View Host")

    def _add_host(self):
        raise NextScene("Add Host")

    def _remove_host(self):
        raise NextScene("Delete Host")

    def _add_command(self):
        raise NextScene("Add Command")

    def _options_command(self):
        raise NextScene("Settings")

    def _exit_command(self):
        def on_close(idx):
            if idx == 0:
                self.model.shutdown()
                sys.exit(0)
            else:
                pass

        dialog = PopUpDialog(self._screen, "Are you sure you want to quit?",
                             buttons=["Yes", "No"],
                             on_close=on_close)
        self._scene.add_effect(dialog)

    # ====================================
    # Overridden functions
    # ====================================

    def _update(self, frame_no):
        if self._ui.theme != self._theme:
            self.set_theme(self._ui.theme)
        self._reload_page()
        super()._update(frame_no)

    def set_theme(self, theme):
        super().set_theme(theme)
        self._theme = theme

    @property
    def frame_update_count(self):
        # Update every 2 seconds
        update = 2
        return update * 20

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, new):
        if isinstance(new, int) and new != 0:
            self._refresh_rate = new


class LogMenu(Frame):

    MAX_LOG_COUNT = 50

    def __init__(self, screen, model: ModelController, logger: LoggingController, ui: UIController):
        super(LogMenu, self).__init__(screen, screen.height//4, screen.width, hover_focus=True,
                                      can_scroll=False, on_load=None,
                                      title="Logs", y=screen.height * 3 // 4)
        self._logger: LoggingController = logger
        self._model: ModelController = model
        self._ui: UIController = ui
        self._last_frame = 0
        self._refresh_rate = 2
        self._theme = None
        self.set_theme(ui.theme)

        # Initialize Widgets
        self._log_list = ListBox(Widget.FILL_FRAME, [], add_scroll_bar=True)
        self._button = Button("Test", on_click=self._reload_frame)

        # Fix Widgets
        layout = Layout([1])
        self.add_layout(layout)
        layout.add_widget(self._log_list)
        # layout.add_widget(self._button)
        self._layout = layout

        # Fix the layouts to the Frame
        self.fix()

    def _reload_frame(self):
        new_logs = self._logger.get_messages()
        count = len(self._log_list.options)
        rendered_logs = [(msg, i) for i, msg in enumerate(new_logs, start=count)]
        if len(self._log_list.options) > self.MAX_LOG_COUNT:
            self._log_list.options = rendered_logs
        else:
            self._log_list.options.extend(rendered_logs)

        # This is the selected value that has focus on the widget
        # see https://github.com/peterbrittain/asciimatics/blob/master/asciimatics/widgets.py#L2545
        if len(self._log_list.options) > 0 and not self._log_list._has_focus:
            self._log_list.value = self._log_list.options[-1][1]

    # ====================================
    # Overridden functions
    # ====================================

    @property
    def frame_update_count(self):
        # Update every 2 seconds
        return 40

    @property
    def refresh_rate(self):
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, new):
        if isinstance(new, int) and new != 0:
            self._refresh_rate = new

    def _update(self, frame_no):
        if self._ui.theme != self._theme:
            self.set_theme(self._ui.theme)
        self._reload_frame()
        super()._update(frame_no)

    def set_theme(self, theme):
        super().set_theme(theme)
        self._theme = theme
