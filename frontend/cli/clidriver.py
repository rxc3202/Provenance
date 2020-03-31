from frontend.cli.menus import *
from frontend.cli.menus.MainMenu import LogMenu
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import sys
from controllers import ModelController, LoggingController


class ProvenanceCLI(object):

    model: ModelController = None
    logger: LoggingController = None
    last_scene: Scene = None

    @classmethod
    def run(cls):
        def driver(screen, scene):
            scenes = [
                Scene([MainMenu(screen, cls.model), LogMenu(screen, cls.model, cls.logger)], -1, name="Main"),
                Scene([AddMachineMenu(screen, cls.model)], -1, name="Add Host"),
                Scene([DeleteMachineMenu(screen, cls.model)], -1, name="Delete Host"),
                Scene([MachineDetailsMenu(screen, cls.model)], -1, name="View Host"),
                Scene([AddCommandMenu(screen, cls.model)], -1, name="Add Command"),
                Scene([SettingsMenu(screen, cls.model, cls.logger)], -1, name="Settings")
            ]
            screen.play(scenes, stop_on_resize=False, start_scene=scene)

        while True:
            try:
                Screen.wrapper(driver, catch_interrupt=True, arguments=[cls.last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                cls.last_scene = e.scene
