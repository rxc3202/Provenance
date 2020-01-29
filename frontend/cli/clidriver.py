from frontend.cli.menu import Menu


banner = """
Welcome to the ...
 ______                                                           
(_____ \                                                          
 _____) )____  ___  _   _  ____  ____    ____  ____    ____  ____ 
|  ____// ___)/ _ \| | | |/ _  )|  _ \  / _  ||  _ \  / ___)/ _  )
| |    | |   | |_| |\ V /( (/ / | | | |( ( | || | | |( (___( (/ / 
|_|    |_|    \___/  \_/  \____)|_| |_| \_||_||_| |_| \____)\____)
                                Command and Control Platform
"""


class MainMenu(Menu):

    def __init__(self, controller):
        super().__init__("Main Menu", banner)
        self.controller = controller


