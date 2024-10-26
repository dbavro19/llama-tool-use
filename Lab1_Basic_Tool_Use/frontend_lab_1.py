import streamlit as st
import logic_lab_1
from tools_lab_1 import get_tools_pretty
from misc_functions import format_user_messages, format_assistant_messages, trim_chat_history, get_next_key

# title of the streamlit app
st.title(f""":rainbow[Building AI Tools for FSI with Llama]""")


if "messages" not in st.session_state:
    st.session_state.messages = {}



with st.expander("Available Tools", expanded=True):
    tools = get_tools_pretty()
    for tool in tools:
        for name, description in tool.items():
            st.markdown(f"**{name}**: {description}")


for message in st.session_state.messages.values():
    role = message.get('role', 'assistant')  # Default to 'assistant' if role is not specified
    content = message.get('content', [])
    
    if content and isinstance(content, list) and 'text' in content[0]:
        display_text = content[0]['text']
    else:
        display_text = str(content)  # Fallback to string representation if unexpected format
    
    with st.chat_message(role):
        st.markdown(display_text.strip())


 

if userQuery := st.chat_input("What is your question?"):

    with st.chat_message("user"):
        st.markdown(userQuery)
    message = format_user_messages(userQuery)
    message_id = get_next_key(st.session_state.messages)
    st.session_state.messages[message_id] = message

    with st.chat_message("assistant"):
        answer_placeholder = st.empty()
        with st.status("Answering!", expanded=True) as status:
            response = logic_lab_1.converse_with_bedrock(list(st.session_state.messages.values()))
            answer, tool, parameters_used = logic_lab_1.parse_response(response)

            st.markdown(f""" Parameters Used:
                            {parameters_used}
                            """)
            answer_placeholder.markdown(f""" Answer:
                            {answer}
                            """)
            
            status.update(label=f"Tool Used: {tool}", state="complete", expanded=False)

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

