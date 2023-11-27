import streamlit as st
import os
import json
import requests
import time
import uuid
from transformers import AutoTokenizer

#Streaming related code.

global word_num
word_num=0


tokenizer=AutoTokenizer.from_pretrained("./")
def get_word(process_id,base_url):
    data = {
    'process_id':process_id}

    json_data = json.dumps(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.post(f"{base_url}/get_word_list", data=json_data, headers=headers,timeout=10)
    ret_list=response.json().get('word_list', [])
    return ret_list



# App title
st.set_page_config(page_title="💬 Python Explainer")


# Replicate Credentials
with st.sidebar:
    st.title('💬 Python Explainer')

    st.subheader('Model parameters')
    # temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    # top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=32, max_value=1024, value=128, step=8)
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
            # response = generate_llama2_response(prompt)
            # placeholder = st.empty()
            # full_response = ''
            # for item in response:
            #     full_response += item
            #     placeholder.markdown(full_response)
            # placeholder.markdown(full_response)

            process_id = str(uuid.uuid4())
            #process_id="bbb"

            base_url="http://f848-34-147-75-119.ngrok.io"
            
            placeholder = st.empty()

            prompt_input=prompt
            max_length=max_length
            data = {
                'prompt': prompt_input,
                'max_length': max_length,
                'process_id':process_id}

            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(f"{base_url}/start_word_generation", data=json_data, headers=headers,timeout=10)

            time.sleep(10)
            ret_list=get_word(process_id,base_url)
            #former_str=""

            while 2 not in ret_list:
                ret_list=get_word(process_id,base_url)
                
                
                
                words_tok=[]
                for word_tok in ret_list:
                    #full_response += word
                    words_tok.append(word_tok)


                
                full_response=tokenizer.decode(words_tok)
                # diff_str=full_response[len(former_str):]
                # print(f"Diff text={diff_str}")

                if '<EOS>'in full_response:
                    idx_eos=full_response.index('<EOS>')
                    full_response=full_response[:idx_eos]


                placeholder.markdown(full_response)
                #former_str=full_response
                time.sleep(10)

            

    message = {"role": "assistant", "content": full_response}
    st.session_state.messages.append(message)