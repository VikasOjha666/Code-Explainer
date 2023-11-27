import streamlit as st
import os
import json
import requests

# App title
st.set_page_config(page_title="💬 Python Explainer")

max_length=256

# Replicate Credentials
with st.sidebar:
    st.title('💬 Python Explainer')

    st.subheader('Model parameters')
    # temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    # top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=1024, value=256, step=8)
    # st.markdown('📖 Learn how to build this app in this [blog](https://blog.streamlit.io/how-to-build-a-llama-2-chatbot/)!')

# Store LLM generated responses
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "Enter the Python Code you want to understand."}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Enter the Python Code you want to understand."}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Function for generating LLaMA2 response. Refactored from https://github.com/a16z-infra/llama2-chatbot
def generate_llama2_response(prompt_input):
    data = {
    'prompt': prompt_input,
    'max_length': max_length} 

    url="http://cf4f-34-91-139-195.ngrok.io/chat"

    json_data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json_data, headers=headers,timeout=10000)

    if response.status_code == 200:
        resp_received=response.json()
        return resp_received['gen_text']

    else:
        return 'Nothing generated.'
    return 'Nothing generated.'

# User-provided prompt
if prompt := st.chat_input(disabled=False):
    prompt_sp=prompt.split('\n')
    prompt=[]
    for pr in prompt_sp:
        prompt.append(pr)
    prompt='  \n'.join(prompt)


    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        prompt_to_display=f"""```{prompt}```"""
        st.write(prompt_to_display)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item
                placeholder.markdown(full_response)
            placeholder.markdown(full_response)
    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)