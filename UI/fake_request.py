import json
import requests
import time


# while True:

#     prompt_input=f'''a=1
#     b=2
#     c=a+b
#     print("Sum=",c)'''
#     max_length=128
#     data = {
#         'prompt': prompt_input,
#         'max_length': max_length,
#         'process_id':"ccc"}

#     url="http://5133-34-170-138-82.ngrok.io/chat"

#     json_data = json.dumps(data)
#     headers = {'Content-Type': 'application/json'}
#     response = requests.post(url, data=json_data, headers=headers,timeout=10)
#     time.sleep(0.1)

#     if response.status_code == 200:
#         resp_received=response.json()
#         print(resp_received['gen_text'])

#     else:
#         print('Nothing generated.')





#Request the first.

base_url="http://6a79-34-147-75-119.ngrok.io"


prompt_input=f'''a=1
    b=2
    c=a+b
    print("Sum=",c)'''
max_length=128
data = {
    'prompt': prompt_input,
    'max_length': max_length,
    'process_id':"aaa"}

json_data = json.dumps(data)
headers = {'Content-Type': 'application/json'}
response = requests.post(f"{base_url}/start_word_generation", data=json_data, headers=headers,timeout=10)

# # Wait for a while to collect some words
time.sleep(10)  # Sleep for 5 seconds

response = requests.get(f"{base_url}/get_word_list")
word_list = response.json().get('word_list', [])

# process_id="aaa"

# data = {
# 'process_id':process_id}

# json_data = json.dumps(data)
# headers = {'Content-Type': 'application/json'}
# response = requests.post(f"{base_url}/get_word_list", data=json_data, headers=headers,timeout=10)
# word_list = response.json().get('word_list', [])

# Print the word list
print("Word List:")
for word in word_list:
    print(word)