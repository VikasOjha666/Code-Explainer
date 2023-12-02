from flask import Flask, request, jsonify
import threading
import time
from flask_ngrok import run_with_ngrok
import copy

from peft import PeftConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from transformers import (
             AutoTokenizer,
             AutoModelForCausalLM,
             LogitsProcessorList,
             MinLengthLogitsProcessor,
            StoppingCriteriaList,
             MaxLengthCriteria,
        )
import torch




config = PeftConfig.from_pretrained("vikasojha/python-code-explainer")
model = AutoModelForCausalLM.from_pretrained("NousResearch/Llama-2-7b-chat-hf")
model = PeftModel.from_pretrained(model, "vikasojha/python-code-explainer")



logits_processor = LogitsProcessorList(
          [
                 MinLengthLogitsProcessor(10, eos_token_id=model.generation_config.eos_token_id),
            ]
        )

# model=model.to("cuda")

tokenizer = AutoTokenizer.from_pretrained('NousResearch/Llama-2-7b-chat-hf')

app = Flask(__name__)
run_with_ngrok(app)

global word_process_dict

# Create a thread-safe list to store words
word_process_dict = {}

# Function to continuously generate and append words

def start_generation(process_id,prompt,max_length=128):

  global word_process_dict

  if process_id in word_process_dict:
     return "AlreadyPresent"
  else:
    word_process_dict[process_id]=[]

    prefix=""
    inputs = tokenizer(
                prefix + prompt, padding=False, add_special_tokens=False, return_tensors="pt"
            )
    inputs["prompt_text"] = prompt

    input_ids = inputs["input_ids"]

    input_ids_c=input_ids.clone()

    pad_token_id = model.generation_config.pad_token_id
    eos_token_id = model.generation_config.eos_token_id


    count=0

    dec_input_ids=torch.tensor([[]])

    decoded_tokens=torch.tensor([[[]]])

    out_tok=[]
    past_key_val=None

    while count<=max_length:
      if count==0:
        #Prepare the input.
        input_dict={}
        input_dict["input_ids"]=input_ids_c
        input_dict["position_ids"]=None
        input_dict["past_key_values"]=past_key_val
        input_dict["use_cache"]=None
        input_dict["attention_mask"]=None

        outputs=model(**input_dict)
      else:
        input_dict={}
        input_dict["input_ids"]=dec_input_ids
        input_dict["position_ids"]=None
        input_dict["past_key_values"]=past_key_val
        input_dict["use_cache"]=None
        input_dict["attention_mask"]=None
        outputs=model(**input_dict)
      next_token_logits = outputs.logits[:, -1, :]
      next_tokens_scores = logits_processor(input_ids, next_token_logits)
      past_key_val=outputs.past_key_values

      next_tokens = torch.argmax(next_tokens_scores, dim=-1)
      if next_tokens==2:
        break
      out_tok.append(next_tokens)
      to_cat=next_tokens[:, None].to(torch.int32)
      decoded_tokens = torch.cat([decoded_tokens, to_cat[:, None]], dim=-1)
      decoded_tokens=decoded_tokens.to(torch.int32)

      dec_input_ids=next_tokens[:, None].to(torch.int32)

      # word=tokenizer.decode(dec_input_ids[0])
      word=dec_input_ids[0].item()

      if count>9:
        word_process_dict[process_id].append(word)

      if word==2:
        break


      count+=1

    word_process_dict[process_id].append(2)



@app.route('/start_word_generation', methods=['POST'])
def start_word_generation():
    global word_process_dict
    # Start the word generation process in a separate thread.
    data=request.get_json()
    process_id=data["process_id"]
    print(f"Process id in start_word_gen={process_id}")
    prompt=data['prompt']
    max_length=data['max_length']

    if process_id in word_process_dict:
      return jsonify({"message": "AlreadyPresent."})
    # else:
    #   word_process_dict[process_id]=[]


    word_generation_thread = threading.Thread(target=start_generation,args=(process_id,prompt,max_length))
    word_generation_thread.daemon = True
    word_generation_thread.start()
    return jsonify({"message": "Word generation process started"})

@app.route('/get_word_list', methods=['POST'])
def get_word_list():
    # Create a copy of the word list for safe retrieval
    data=request.get_json()
    process_id=data["process_id"]
    print(f"Process id in get_word_list={process_id}")
    word_list_copy = copy.copy(word_process_dict[process_id])
    #print(word_list_copy)
    return jsonify({"word_list": word_list_copy})

if __name__ == '__main__':
    app.run()
