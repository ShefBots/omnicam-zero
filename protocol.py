from enum import Enum

SLEEP_TIME = 1

class Mode(Enum):
    TIME = "T" # Transmits the time sporadically
    RANDOM = "R" # Transmits a random number sporadically
    STOP = "S" # Perminently stops the server
    PAUSE = "P" # Puts the server into a low-CPU "paused" state. May take up to SLEEP_TIME seconds before waking

