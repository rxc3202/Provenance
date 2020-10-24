from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, \
    Button, TextBox, Widget, MultiColumnListBox, PopUpDialog, DropdownList
from asciimatics.exceptions import NextScene
from util.structs import ClientInfo
from controllers import *
import sys
from util.validators import ip_validator, hostname_validator


class MainMenu(Frame):

    def __init__(self, screen, model: ModelController, ui: UIController):
        super(MainMenu, self).__init__(screen,
                                       height=screen.height * 3 // 4,
                                       width=screen.width * 3 // 4,
                                       hover_focus=True,
                                       can_scroll=False,
                                       on_load=self._reload_page,
                                       title="Main Menu",
                                       x=0,
                                       y=0)
        self.model: ModelController = model
        self._ui: UIController = ui
        self._screen = screen
        self._last_frame = 0
        self._theme = None
        self.set_theme(ui.theme)

        # Init all widgets
        self._machine_list_widget = self._init_machine_list_widget()
        self._add_host_button = Button("Add Host", self._add_host)
        # self._rem_host_button = Button("Remove Host", self._remove_host)
        self._add_cmd_button = Button("Add CMD", self._add_command)
        self._rem_cmd_button = Button("Settings", self._options_command)
        self._refresh_button = Button("Create Backup", self._refresh)
        self._exit_button = Button("Exit", self._exit_command)

        # Generation
        details_layout = Layout([1], fill_frame=True)
        self.add_layout(details_layout)
        details_layout.add_widget(self._machine_list_widget)
        details_layout.add_widget(Divider())

        button_layout = Layout([1, 1, 1, 1, 1])
        self.add_layout(button_layout)
        button_layout.add_widget(self._refresh_button, 0)
        button_layout.add_widget(self._add_host_button, 1)
        # button_layout.add_widget(self._rem_host_button, 2)
        button_layout.add_widget(self._add_cmd_button, 2)
        button_layout.add_widget(self._rem_cmd_button, 3)
        button_layout.add_widget(self._exit_button, 4)

        self._details_layout = details_layout
        self._button_layout = button_layout
        # Confirm Frame
        self.fix()

    # Widget Initializations

    def _init_machine_list_widget(self):
        machines = self.model.displayed_machines

        fields = ["Type", "OS", "Hostname", "IP", "Last Active", "Next Command"]
        widths = ["<10%", "<10%", "<25%", "<15%", "<10%", "<30%"]
        # old = [f"<{100 // len(fields)}%" for _ in fields]
        return MultiColumnListBox(
            height=Widget.FILL_FRAME,
            columns=widths,
            options=[(x, i) for i, x in enumerate(machines)],
            titles=fields,
            add_scroll_bar=True,
            on_select=self._view_host,
            name="machines"
        )

    # Backend Methods

    def _reload_page(self):
        machines = self.model.displayed_machines
        # machines = [("1", "2", "3", "4", "5", "6")]
        # TODO: make a more efficient way to propogate changes so we dont reload the list every time
        tmp = self._machine_list_widget.value
        self._machine_list_widget.options = [(x, i) for i, x in enumerate(machines)]
        self._machine_list_widget.value = tmp

    # Menu Actions Methods
    def _refresh(self):
        self.model.backup()
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
        return self._ui.refresh_rate * 20


class FilterMenu(Frame):
    reset_data = {"beacon": None, "ips": '', "active": '', "hostname": '', "os": None}

    def __init__(self, screen, model: ModelController, ui: UIController):
        super(FilterMenu, self).__init__(screen,
                                         height=screen.height * 3 // 4,
                                         width=screen.width * 1 // 4 + 1,
                                         hover_focus=True,
                                         can_scroll=False,
                                         on_load=None,
                                         title="Filter",
                                         x=screen.width * 3 // 4,
                                         y=0)
        self._model: ModelController = model
        self._ui: UIController = ui

        # Initialize Widgets
        self._clear_button = Button("Clear", on_click=self._clear_filters, add_box=True)
        self._apply_button = Button("Apply", on_click=self._apply, add_box=True)
        self._beacon_header = Text(disabled=True)
        self._beacon_header.value = "Beacon Type: "
        self._beacon_type = DropdownList(
            [("All", None), ("DNS", "DNS"), ("HTTP", "HTTP"), ("ICMP", "ICMP")],
            name="beacon"
        )

        self._active_header = Text(disabled=True)
        self._active_header.value = "Last Active (in minutes): "
        self._active_field = Text(name="active")

        self._ip_header = Text(disabled=True)
        self._ip_header.value = "IPs and/or subnet(s): "
        self._ip_input = Text(name="ips")

        self._hostname_header = Text(disabled=True)
        self._hostname_header.value = "Hostname: "
        self._hostname_input = Text(name="hostname")

        self._os_header = Text(disabled=True)
        self._os_header.value = "OS: "
        self._os_input = DropdownList(
            [("All", None), ("Linux", "linux"), ("Windows", "windows")],
            name="os"
        )

        self._filler = TextBox(Widget.FILL_FRAME, disabled=True)
        # Default values
        self._active_field.value = None
        self._ip_input.value = None

        # Add Widgets to Frame
        layout = Layout([1], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(self._beacon_header)
        layout.add_widget(self._beacon_type)
        layout.add_widget(self._os_header)
        layout.add_widget(self._os_input)
        layout.add_widget(self._active_header)
        layout.add_widget(self._active_field)
        layout.add_widget(self._ip_header)
        layout.add_widget(self._ip_input)
        layout.add_widget(self._hostname_header)
        layout.add_widget(self._hostname_input)

        layout.add_widget(self._filler)
        layout.add_widget(Divider())

        buttons = Layout([1, 1])
        self.add_layout(buttons)
        buttons.add_widget(self._apply_button, 0)
        buttons.add_widget(self._clear_button, 1)

        # Fix all widgets to Frame
        self.fix()

    def save(self, validate=False):
        super().save(validate)
        # Encoding raw strings for regex only
        raw = self.data["hostname"].encode('unicode-escape').decode()
        self.data["hostname"] = raw

    def _validate(self):
        def fail(msg):
            dialog = PopUpDialog(self._screen, f"  {msg}  ", buttons=["OK"], theme="warning")
            self._scene.add_effect(dialog)
            return False

        self.save()
        if self.data["ips"]:
            failure = ip_validator(self.data["ips"])
            if failure:
                fail(f"Invalid IP or subnet: {failure} in Filter Menu")
                return False
        if self.data["hostname"]:
            if not hostname_validator(self.data["hostname"]):
                fail(f"Invalid Python3 regex: {self.data['hostname']}")
                return False
        return True

    def _apply(self):
        self.save()
        if not self._validate():
            return
        self._model.filters = self.data

    def _clear_filters(self):
        self.reset()
        self.data = self.reset_data
        # Do this to refresh the screen
        self._model.filters = self.data

    def _help(self):
        pass

    # ====================================
    # Overridden functions
    # ====================================

    @property
    def frame_update_count(self):
        # Update every 2 seconds
        return self._ui.refresh_rate * 20

    def _update(self, frame_no):
        if self._ui.theme != self._theme:
            self.set_theme(self._ui.theme)
        super()._update(frame_no)

    def set_theme(self, theme):
        super().set_theme(theme)
        self._theme = theme


class LogMenu(Frame):
    MAX_LOG_COUNT = 50

    def __init__(self, screen, model: ModelController, logger: LoggingController, ui: UIController):
        super(LogMenu, self).__init__(screen,
                                      height=screen.height // 4,
                                      width=screen.width,
                                      hover_focus=True,
                                      can_scroll=False,
                                      on_load=None,
                                      title="Logs",
                                      y=screen.height * 3 // 4)
        self._logger: LoggingController = logger
        self._model: ModelController = model
        self._ui: UIController = ui
        self._last_frame = 0
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
        return self._ui.refresh_rate * 20

    def _update(self, frame_no):
        if self._ui.theme != self._theme:
            self.set_theme(self._ui.theme)
        self._reload_frame()
        super()._update(frame_no)

    def set_theme(self, theme):
        super().set_theme(theme)
        self._theme = theme
