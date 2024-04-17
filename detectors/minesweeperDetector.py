import random
import math
import asyncio

def get_data_format_info():
    return {
                "angle": "Normalised angle of the mine, counter-clockwise from the north/forward heading of the robot, 0-1",
                "dist": "Distance to the mine in mm",
                "on": "Boolean indicating if the mine is currently under the robot"
            }

def get_data():
    distance = random.random() * 300
    return {
            "angle": random.random(),
            "dist": distance,
            "on" : distance < 50
           }

