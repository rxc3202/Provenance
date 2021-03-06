from enum import Enum
from collections import namedtuple
import json


class CommandType(Enum):
    """ The types of commands that can be on the victim

    * NOP = Do nothing
    * POWERSHELL = Run something in powershell
    * CMD = Run Something in cmd

    """
    NOP = 0
    PS = 1
    CMD = 2
    BASH = 3

    @classmethod
    def encode(cls, key):
        d = {
            cls.NOP: "none",
            cls.PS: "ps",
            cls.CMD: "cmd",
            cls.BASH: "bash"
        }
        return d[key]

    @classmethod
    def decode(cls, encoded_key: str):
        d = {
            "none": cls.NOP,
            "ps": cls.PS,
            "cmd": cls.CMD,
            "bash": cls.BASH
        }
        return d[encoded_key]


"""
A simple class allowing for a more intuitive semantic understanding
of the commands passed between parts of the Provenance server rather than
accessing them using indices
"""


class Command(object):
    __slots__ = ["_type", "_command", "_uid"]
    _keys = [x.replace('_', '') for x in __slots__]

    def __init__(self, cmd_type, command="", uid=None):
        self._type: CommandType = cmd_type
        self._command: str = command
        self._uid = uid

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, new):
        if isinstance(new, CommandType):
            self._type = new
        elif isinstance(new, str):
            self._type = CommandType.decode(new)
        else:
            pass

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, new):
        self._command = new

    @property
    def uid(self):
        return self._uid

    @staticmethod
    def encode(command):
        """
        Encodes into JSON usable format
        :param command: the Command to encode
        :return: a python dict used for JSON encoding
        """
        return {
            "type": CommandType.encode(command.type),
            "command": command.command,
            "uid": command.uid
        }

    @staticmethod
    def decode(json_command):
        """
        Decodes a Command object from JSON format (as a string) and reproduces
        the original Command instance
        :param json_command: a string with the keys defined in Command._keys
        :return: a Command object
        """
        if isinstance(json_command, str):
            d: dict = json.loads(json_command)
            # check if there are all expected keys to create a new command
            if set(d.keys()) == set(Command._keys):
                return Command(d["type"], d["command"], d["uid"])
            return None
        elif isinstance(json_command, dict):
            return Command(json_command["type"],
                           json_command["command"],
                           json_command["uid"]
                           )
        else:
            return None


"""
A simple structure allowing for a more intuitive semantic understanding
of the information queried from server representation of the clients rather than
accessing them using indices
"""
ClientInfo = namedtuple("ClientInfo", ["beacon", "state", "os", "hostname", "ip", "active", "commands", "uuid"])
