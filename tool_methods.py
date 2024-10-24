import json
import random

#Tool Methods

#method to generate random number between 1 and 100
def random_number_1_to_100():
    random_number = random.randint(1, 100)
    return random_number

#method to generate random number within a specified range
def random_number_with_inputs(min, max):
    random_number = random.randint(min, max)
    return random_number

