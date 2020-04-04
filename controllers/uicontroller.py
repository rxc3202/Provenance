from asciimatics.widgets import THEMES as ASCIIMATICS_THEMES


class UIController(object):

    def __init__(self):
        self._refresh_rate = 2
        self._theme = "default"
        self._show_logs = True

    @property
    def refresh_rate(self):
        return self.refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, new):
        self.refresh_rate = new

    @property
    def theme(self):
        return self._theme

    @theme.setter
    def theme(self, new: str):
        if new not in ASCIIMATICS_THEMES:
            return
        else:
            self._theme = new

    @property
    def show_logs(self):
        return self._show_logs

    @show_logs.setter
    def show_logs(self, new: bool):
        self._show_logs = new
