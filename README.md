# Code-Explainer

This is the UI,training and inference server code repo for the code explainer that I created 
to explain me the python code in the same tone as chatGPT does.

### Requirements.
- peft==0.4.0
- transformers==4.31.0
- streamlit==1.29.0
- tokenizers=0.13.3
- flask
- flask-ngrok
- pytorch

### How to setup the server and Client.
- Setup the dependencies.
- Run the backend server with `python server.py` on a machine.
- Change the value of base_url in line 86 of UI_streaming file.
- Run the UI with `python UI_streaming.py`


