from frontend.cli.menus.welcome import WelcomeMenu


class CLIDriver(object):

    def __init__(self, init_menu):
        self.current_menu = init_menu

    def switch_menu(self, menu):
        self.current_menu = menu

    def run(self):
        while True:
            self.current_menu.print_banner()
            self.current_menu.display_actions()
            self.current_menu.act()

    @staticmethod
    def generate():
        main_menu = WelcomeMenu.generate()
        return CLIDriver(main_menu)


