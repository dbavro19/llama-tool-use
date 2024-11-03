import boto3
import json
import time
import requests
import os
from typing import Dict, List, Callable
import streamlit as st
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from stock_tool import get_stock_price
from monte_carlo_tool import monte_carlo_simulator
from tools_lab_2 import get_tools



# Tool definitions - each tool is just a function
def stock_tool(stock_symbol: str, user_question: str, get_52_week_details: bool) -> str:
    """Gets current price and the 52 week high or low (if get_52_week_details = True) for requested financial instrument or stock """
    results = get_stock_price(stock_symbol, user_question, get_52_week_details, return_to_llm=False)
    return f"{stock_symbol} pricing information: {results}"

def monte_carlo_tool(initial_value: int, years: int = 10, num_simulations: int = 100,annual_return: int = 7, annual_volatility: int = 12 ) -> json:
    """Run monte carlo simulation with specified inputs - returns graph plot as json"""
    fig = monte_carlo_simulator(initial_value, years, num_simulations, annual_return, annual_volatility)
    return fig.to_json()



# Tool registry
TOOLS = {
    "stock_tool": stock_tool,
    "monte_carlo_tool": monte_carlo_tool
}

def get_tool_descriptions() -> str:
    """Generate descriptions of available tools"""
    descriptions = []
    for name, func in TOOLS.items():
        descriptions.append(f"- {name}: {func.__doc__}")
    return "\n".join(descriptions)

def create_plan(client: boto3.client, goal: str) -> Dict:
    """Generate a plan that includes tool usage"""
    tools_desc = get_tool_descriptions()
    planning_prompt = f"""
    Create a plan to achieve this goal: {goal}
    
    Available tools:
    {tools_desc}
    
    Return a JSON object with this exact structure:
    {{
        "goal": "the main goal",
        "steps": [
            {{
                "description": "step description",
                "tool": "tool_name or null if no tool needed",
                "tool_args": "arguments for the tool if needed"
            }}
        ]
    }}

    
    
    Include specific tool usage where appropriate.
    """
    

    prompt = {
        "anthropic_version":"bedrock-2023-05-31",
        "max_tokens":30000,
        "temperature":0,
        "messages":[
            {
                "role":"user",
                "content":[
                    {  
                        "type":"text",
                        "text": planning_prompt
                    }
                ]
            }
        ]
    }

    json_prompt = json.dumps(prompt)



    response = client.invoke_model(body=json_prompt, modelId="anthropic.claude-3-sonnet-20240229-v1:0", accept="application/json", contentType="application/json")

    results = json.loads(response.get('body').read())
    
    return results

def execute_step(client: boto3.client, step: Dict) -> str:
    """Execute a single step, using tools if specified"""
    # If step requires a tool, execute it
    if step.get("tool") and step["tool"] in TOOLS:
        tool_result = TOOLS[step["tool"]](step["tool_args"])
        
        # Let the agent interpret the tool result
        execution_prompt = f"""
        Step: {step['description']}
        Tool used: {step['tool']}
        Tool result: {tool_result}
        
        Interpret the tool result and provide next actions if needed.
        """
    else:
        # Regular step execution without tools
        execution_prompt = f"""
        Execute this step: {step['description']}
        Provide specific, actionable instructions or results.
        """
    
    response = client.messages.create(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        max_tokens=500,
        messages=[{"role": "user", "content": execution_prompt}]
    )
    
    return response.content

def run_agent(api_key: str, goal: str) -> List[Dict]:
    """Run the entire planning and execution process with tools"""
    bedrock =boto3.client('bedrock-runtime', region_name='us-west-2')
    
    # Create plan
    st.write("Using a plan and execute agent")
    st.write("Generating Plan")
    plan = create_plan(bedrock, goal)
    results = []
    
    # Execute each step
    for i, step in enumerate(plan["steps"], 1):
        print(f"\nExecuting step {i}: {step['description']}")
        result = execute_step(bedrock, step)
        results.append({
            "step": step["description"],
            "tool_used": step.get("tool"),
            "result": result
        })
        time.sleep(1)  # Basic rate limiting
        
    return results

# Example usage
if __name__ == "__main__":
    goal = "Run a monte carlo simulation for a 7 year period on the 52 week high apple stock"
    results = run_agent("your-api-key", goal)
    
    # Print results
    print("\nExecution Results:")
    for i, result in enumerate(results, 1):
        print(f"\nStep {i}: {result['step']}")
        if result.get("tool_used"):
            print(f"Tool Used: {result['tool_used']}")
        print(f"Result: {result['result']}")