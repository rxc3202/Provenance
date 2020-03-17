from enum import Enum
from collections import namedtuple


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


"""
A simple structure allowing for a more intuitive semantic understanding
of the commands passed between parts of the Provenance server rather than
accessing them using indices
"""
Command = namedtuple("Command", ["type", "command", "uid"])




