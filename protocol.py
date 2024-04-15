from enum import Enum

COMMUNICATION_PORT = 1337

class Mode(Enum):
    TIME = "T" # Transmits the time sporadically
    RANDOM = "R" # Transmits a random number sporadically
    TASK_MINESWEEPER = "M" # Starts detecting minesweeper objects
    STOP = "S" # (the last one) Perminently stops the server

MODE_STRINGS = [mode.value for mode in Mode]

def get_mode_description(m):
    return {
        Mode.TIME: "Transmits the time sporadically",
        Mode.RANDOM: "Transmits a random number sporadically",
        #Mode.PAUSE: "Puts the server into a low-CPU 'paused' state. May take up to SLEEP_TIME seconds before waking",
        Mode.TASK_MINESWEEPER: "Starts detecting minesweeper objects",
        Mode.STOP: "Perminently stops the server"
    }[m]
