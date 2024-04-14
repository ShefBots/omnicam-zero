from enum import Enum

SLEEP_TIME = 1

class Mode(Enum):
    TIME = "T" # Transmits the time sporadically
    RANDOM = "R" # Transmits a random number sporadically
    PAUSE = "P" # Puts the server into a low-CPU "paused" state. May take up to SLEEP_TIME seconds before waking
    TASK_MINESWEEPER = "M" # Starts detecting minesweeper objects
    STOP = "S" # (the last one) Perminently stops the server
