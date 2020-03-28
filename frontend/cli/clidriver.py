from frontend.cli.menus import *
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
import sys


class ProvenanceCLI(object):

    model = None
    last_scene = None

    @classmethod
    def run(cls):
        def driver(screen, scene):
            scenes = [
                Scene([MainMenu(screen, cls.model)], -1, name="Main"),
                Scene([MainMenu(screen, cls.model), AddMachineMenu(screen, cls.model)], -1, name="Add Host"),
                Scene([MainMenu(screen, cls.model), DeleteMachineMenu(screen, cls.model)], -1, name="Delete Host"),
                Scene([MachineDetailsMenu(screen, cls.model)], -1, name="View Host"),
            ]
            screen.play(scenes, stop_on_resize=False, start_scene=scene)

        while True:
            try:
                Screen.wrapper(driver, catch_interrupt=True, arguments=[cls.last_scene])
                sys.exit(0)
            except ResizeScreenError as e:
                cls.last_scene = e.scene
