


import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st

from misc_functions import call_llm, parse_xml


# ----------------------------------This Tool Takes inputs for and runs a Monte Carlo Simulation and plots it ----------------------------------
# ------------------------------------------------------- Fully Deterministic ------------------------------------------------------------------


def get_monte_carlo():
    insurance_and_account_frequently_asked_questions = {
        "toolSpec": {
            "name": "monte_carlo_simulator",
            "description": "generates and graphs a Monte Carlo Simulation for investment projection",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "initial_value": {
                            "type": "number",
                            "description": "The initial investment or value in dollars"
                        },
                        "years": {
                            "type": "number",
                            "description": "the investment period in years"
                        },
                        "num_simulations": {
                            "type": "number",
                            "description": "The number of simulations to run"
                        },
                        "annual_return": {
                            "type": "number",
                            "description": "the expected rate of annual return as a percentage value"
                        },
                        "annual_volatility":{
                            "type": "number",
                            "description": "the expected rate of annual volatility as a percentage value"
                        }
                    },
                    "required": ["initial_investment"]
                }
            }
        }
    }
    return insurance_and_account_frequently_asked_questions


def monte_carlo_simulator(initial_value, years=10, num_simulations=100, annual_return=7, annual_volatility = 12):
    #check inputs for ints
    initial_investment = int(initial_value)
    years = int(years)
    num_simulations = int(num_simulations)
    annual_return = int(annual_return)/100
    annual_volatility = int(annual_volatility) / 100

    st.write("Running Simulations")

    # Run simulations
    ending_values = []
    for _ in range(num_simulations):
        # simulate each year as a random return
        returns = np.random.normal(annual_return, annual_volatility, years)
        # compound investment over time
        final_value = initial_investment * np.prod(1 + returns)
        ending_values.append(final_value)

    st.write("Visualizing Results")

    # Analyze and visualize results
    fig = go.Figure(data=[go.Histogram(x=ending_values, nbinsx=50)])

    # Update layout for readability
    fig.update_layout(
        title=f'{years}-Year Investment Simulation',
        xaxis_title='Ending Value',
        yaxis_title='Frequency',
        bargap=0.1
    )

    # Return plot
    return fig
