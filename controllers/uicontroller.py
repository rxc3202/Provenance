from asciimatics.widgets import THEMES as ASCIIMATICS_THEMES


class UIController(object):

    def __init__(self):
        self._refresh_rate = 2
        self._theme = "default"
        self._show_logs = True

    @property
    def refresh_rate(self):
        """
        Get the frequency (in seconds) of how often the UI should query the model for
        its information
        :return:
        """
        return self._refresh_rate

    @refresh_rate.setter
    def refresh_rate(self, new: int):
        """
        Set the refresh rate of the UI
        :param new: an int representing the frequency in seconds
        :return: None
        """
        if isinstance(new, int) and new != 0:
            self._refresh_rate = new

    @property
    def theme(self):
        """
        Return the string that represents the theme
        :return: a string from asciimatics.widgets.Themes
        """
        return self._theme

    @theme.setter
    def theme(self, new: str):
        """
        A string in asciimatics.widgets.THEMES
        :param new: the string
        :return:
        """
        if new not in ASCIIMATICS_THEMES:
            return
        else:
            self._theme = new
