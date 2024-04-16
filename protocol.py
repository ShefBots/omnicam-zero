from enum import Enum

COMMUNICATION_PORT = 1337
REMOTE_ADDR = "192.168.22.1"

class Mode(Enum):
    TIME = "T" # Transmits the time sporadically
    RANDOM = "R" # Transmits a random number sporadically
    TASK_MINESWEEPER = "M" # Starts detecting minesweeper objects
    STOP = "S" # (the last one) Perminently stops the server

    def __str__(self):
        return self.value

MODE_STRINGS = [mode.value for mode in Mode]

def get_mode_description(m):
    return {
        Mode.TIME: "Transmits the time sporadically",
        Mode.RANDOM: "Transmits a random number sporadically",
        Mode.TASK_MINESWEEPER: "Starts detecting minesweeper objects",
        Mode.STOP: "Perminently stops the server"
    }[m]

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
        Mode.STOP: "TRANSMITS NO DATA"
    }[m]
