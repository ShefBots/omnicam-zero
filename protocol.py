from enum import Enum
from functools import reduce

COMMUNICATION_PORT = 1337
REMOTE_ADDR = "192.168.22.1"

MODE_IDENTIFIER_INDICATOR = "M" # Name of field affixed to every transmission that indicates mode

class Mode(Enum):
    TIME = "T" # Transmits the time sporadically
    RANDOM = "R" # Transmits a random number sporadically
    TASK_MINESWEEPER = "M" # Starts detecting minesweeper objects
    TASK_LAVA_PALAVA = "L" # Starts detecting an offset line
    TASK_ECO_DISASTER = "E" # Starts detecting barrels and end goals and stuff

    def __str__(self):
        return self.value

MODE_STRINGS = [mode.value for mode in Mode]

_mode_string_to_enum = reduce(lambda obj, n: obj | {n[0]: n[1]}, zip([m.value for m in Mode], Mode), {})
mode_string_to_enum = lambda mode_string: _mode_string_to_enum[mode_string]

_mode_to_description = {
                           Mode.TIME: "Transmits the time sporadically",
                           Mode.RANDOM: "Transmits a random number sporadically",
                           Mode.TASK_MINESWEEPER: "Starts detecting minesweeper objects",
                           Mode.TASK_LAVA_PALAVA: "Starts detecting an offset line",
                           Mode.TASK_ECO_DISASTER: "Starts detecting barrels and end goals and stuff",
                       }
get_mode_description = lambda m: _mode_to_description[m]

def get_mode_data_format(m):
    return {
        Mode.TIME:
"""
{
    "datetime": "YYYY-MM-DD HH:MM:SS.SSSSSS"
}
""",
        Mode.RANDOM:
"""
{
    "random": A random number between 0 and 1
}
""",
        Mode.TASK_MINESWEEPER:
"""
DATA FORMAT CURRENTLY UNDEFINED.
""",
        Mode.TASK_LAVA_PALAVA:
"""
DATA FORMAT CURRENTLY UNDEFINED.
""",
        Mode.TASK_ECO_DISASTER:
"""
DATA FORMAT CURRENTLY UNDEFINED.
""",
    }[m]
