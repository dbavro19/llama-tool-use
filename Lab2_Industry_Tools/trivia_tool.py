from datetime import datetime
from misc_functions import call_llm




# ----------------------------- This Tool allows the LLM to call another LLM to perform basic knowledge answering. -------------------------------------- 
# --------------------------------------Useful if you are otherwise forcing the model to only use tools! ----------------------



def get_basic_trivia_tool():
    #Basic Trivia Tool
    basic_trivia_tool = {
        "toolSpec": {
            "name": "basic_trivia_tool",
            "description": "Provides answers for basic triva and other common knowledge that an LLM can reliably answer",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "user_question": {
                            "type": "string",
                            "description": "The most recent question asked by the user question that prompted the tool"
                        }
                    },
                    "required": ["user_question"]
                }
            }
        }
    }

    return basic_trivia_tool





#Method to answer basic trvia - so that we can enforce our model always using tools when it can
def basic_trivia_tool(user_question, return_to_llm=False):

    user_prompt = f"""
    Question: {str(user_question)}

    """

    system_prompt = f"""
    You are a helpful AI assistant that is an expert in trivia and general knowledge. Answer the user's question accurately and concisely

    The Current Date is: {get_current_date_tool()}
    """

    print(f""" 
PRINTING TRIVIA TOOL PROMPTS
          
USER PROMPT: {user_prompt}

SYSTEM PROMPT: {system_prompt}

""")

    results = call_llm(user_prompt, system_prompt)


    return results





def get_current_date_tool():
    now = datetime.now()
    formatted_date = now.strftime("%A %B %d, %Y")

    # Add the ordinal suffix to the day
    day = now.day
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]

    formatted_date = formatted_date.replace(f" {day},", f" {day}{suffix},")

    print(formatted_date)
    return formatted_date
