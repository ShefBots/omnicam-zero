import random


def get_data():
    return {
            "mine_angle": random.random() * math.pi * 2,
            "mine_distance": random.random() * 100,
           }
