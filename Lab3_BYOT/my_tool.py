
import json
import streamlit as st
import requests

def get_weather(city):
    # Log the start of the function
    st.write("Starting get_weather function")
    
    # Define the API endpoint and API key
    api_endpoint = "http://api.openweathermap.org/data/2.5/weather"
    api_key = "89d3c1f4adc6d1c49259fa7ba18f24e7"  # Replace with your OpenWeatherMap API key
    
    # Create the API request parameters
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric"
    }
    
    # Log the API request parameters
    st.write("API request parameters: ", params)
    
    # Make the API request
    response = requests.get(api_endpoint, params=params)
    
    # Log the API response
    st.write("API response: ", response.text)
    
    # Check if the API request was successful
    if response.status_code == 200:
        # Parse the JSON response
        weather_data = json.loads(response.text)
        
        # Extract the weather information
        weather_info = f"Weather in {city}: {weather_data['weather'][0]['description']}, Temperature: {weather_data['main']['temp']}�C, Humidity: {weather_data['main']['humidity']}%"
        
        # Log the weather information
        st.write("Weather information: ", weather_info)
        
        # Return the weather information as a string
        return weather_info
    else:
        # Log the error message
        st.write("Error: ", response.text)
        
        # Return an error message
        return "Failed to retrieve weather information"



def get_tool_method():
    my_tool_spec = '{"toolSpec": {"name": "get_weather", "description": "Retrieves the weather for the specified city", "inputSchema": {"json": {"type": "object", "properties": {"city": {"type": "string", "description": "name of the city that the request specified"}}, "required": ["city"]}}}}'
    my_tool_spec_json = json.loads(my_tool_spec)
    return my_tool_spec_json


