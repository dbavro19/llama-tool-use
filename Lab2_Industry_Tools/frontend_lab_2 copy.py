import streamlit as st
import logic_lab_2
from tools_lab_2 import get_tools_pretty, execute_tool
from misc_functions import format_user_messages, format_assistant_messages, trim_chat_history, get_next_key,get_model, spoof_tool_response, spoof_tool_user_message

# title of the streamlit app
st.title(f""":rainbow[Building AI Tools for FSI with Llama]""")


if "messages" not in st.session_state:
    st.session_state.messages = {}


#Display available tools at the top
with st.expander("Available Tools", expanded=True):
    tools = get_tools_pretty()
    for tool in tools:
        for name, description in tool.items():
            st.markdown(f"**{name}**: {description}")







#Handle past messages and display them
for message in st.session_state.messages.values():
    role = message.get('role', 'assistant')  # Default to 'assistant' if role is not specified
    content = message.get('content', [])
    
    if content and isinstance(content, list) and 'text' in content[0]:
        display_text = content[0]['text']
    else:
        display_text = str(content)  # Fallback to string representation if unexpected format
    
    with st.chat_message(role):
        st.markdown(display_text.strip())


st.divider()

answer_type = "text"

if userQuery := st.chat_input("What is your question?"):

    #input question  and store that in user message format
    with st.chat_message("user"):
        st.markdown(userQuery)
    message = format_user_messages(userQuery)
    message_id = get_next_key(st.session_state.messages)
    st.session_state.messages[message_id] = message

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        with st.status("Answering!", expanded=True) as status:
            response = logic_lab_2.converse_with_bedrock_with_tools(list(st.session_state.messages.values()))
            

            tool_used, true_tool_use, tool_name, tool_use_id, parameters_used, answer = logic_lab_2.parse_response(response)

            print(f"TOOL USED = {tool_used}")
            print(f"TRUE TOOL USE = {true_tool_use}")
            print(f"TOOL NAME = {tool_name}")
            print(f"TOOL USE ID = {tool_use_id}")
            print(f"PARAMETERS USED = {parameters_used}")

            

            if tool_used == True:

                if true_tool_use == False:
                    print("RETRYING MODEL CALL AS IT DIDNT FORMAT THE TOOL CORRECTLY")
                    retry_model= get_model()
                    response = logic_lab_2.converse_with_bedrock_with_tools(list(st.session_state.messages.values()), model_id=retry_model)

                st.write(f"Using Tool : {tool_name}")


                tool_answer, answer_type, return_to_llm_string = execute_tool(tool_name, parameters_used)



                if isinstance(return_to_llm_string, bool):
                    return_to_llm = return_to_llm_string
                else:
                    return_to_llm = eval(return_to_llm_string)

                


                if return_to_llm == True:
                    
                    
                    #Handle messaging for tool response

                    if true_tool_use == True:

                        print("RETURNING TO LLM")
                        status.write(f""" Initial Tool Used: {tool_name}""")

                        status.write(f""" Parameters Used: {parameters_used}""")
                        status.write(f""" Tool Response: {tool_answer}""")
                        status.write(f""" Sending Response Back to LLM""")


                        temp_assistant_message = spoof_tool_response(tool_use_id, tool_name, parameters_used)

                        #Adding tool execution as message
                        message_id = get_next_key(st.session_state.messages)
                        st.session_state.messages[message_id] = temp_assistant_message

                        #fomrating tool response as a model message
                        temp_user_message = spoof_tool_user_message(tool_use_id,answer_type, tool_answer)
                        #Add the fomred message to the session state
                        message_id = get_next_key(st.session_state.messages)
                        st.session_state.messages[message_id] = temp_user_message

                        response_2 = logic_lab_2.converse_with_bedrock_with_tools(list(st.session_state.messages.values()))

                        tool_used, true_tool_use, tool_name, tool_use_id, parameters_used, answer = logic_lab_2.parse_response(response_2)

                        

                    #call LLM
                
                elif return_to_llm == False:
                    status.update(label=f"Tool Used: {tool_name}", state="complete", expanded=False)

                    status.write(f""" ----------------- Tool Summary --------------------""")

                    status.write(f""" Parameters Used:{parameters_used}""")

                    answer_placeholder.write(f""" Tool Response :{tool_answer}""")
                    
                    answer = tool_answer




            else:
                status.update(label=f"No Tool Used", state="complete", expanded=False)
                status.write(f" Parameters Used: {parameters_used}")
                

            


            #answer, tool, parameters_used = logic_lab_2.parse_response(response)
            if answer_type == "text" or answer_type == "markdown":

                answer_placeholder.write(f" Answer: {answer}")
            
            elif answer_type == "json":

                answer_placeholder.json(answer)

            elif answer_type == "image":

                answer_placeholder.image(answer)

                #answer="image"
            
            elif answer_type == "plotly":

                temp_answer = answer
                answer = "Plotly Graph"


                answer_placeholder.plotly_chart(temp_answer)
                
            

            
            status.update(label=f"Tool Used: {tool_name}", state="complete", expanded=False)

    message_id = get_next_key(st.session_state.messages)
    st.session_state.messages[message_id] = format_assistant_messages(str(answer))

    st.session_state.messages = trim_chat_history(st.session_state.messages)




# TO DO
# I need to add a way to upload documents to the converse method - Lab2?
# Need to add streamlit upload doc to the streamlit frontend - Lab2?
# Need to add conversation history - Done
# Need to add continuous chat - Done
#Clean up the basic_tools_file - Done
#rename everything - Done

