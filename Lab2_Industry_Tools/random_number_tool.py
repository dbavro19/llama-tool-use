import random



def get_random_number_tool():
    #random number tool - this time we will feed the result back to the model
    random_number_1_to_100_tool = {
        "toolSpec": {
            "name": "random_number_1_to_100",
            "description": "Generate a random number between 1 and 100 - use this as the default number generation tool if no minimum or maximum range is specified.",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {},
                }
            }
        }
    }

    return random_number_1_to_100_tool




#method to generate random number between 1 and 100
def random_number_1_to_100(return_to_llm=True):
    random_number = random.randint(1, 100)
    return random_number