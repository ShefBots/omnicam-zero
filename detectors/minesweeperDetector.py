import random
import math
import asyncio

def get_data_format_info():
    return {"NOTICE:": "DATA FORMAT CURRENTLY UNDEFINED."}

def get_data():
    asyncio.sleep(0.4) # Simulate longer processing delay
    return {
            "mine_angle": random.random() * math.pi * 2,
            "mine_distance": random.random() * 100
           }

