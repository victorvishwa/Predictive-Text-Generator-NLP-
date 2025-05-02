from flask import Flask, render_template, request, jsonify
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re

app = Flask(__name__)

# Load GPT-2 model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
gpt2 = GPT2LMHeadModel.from_pretrained(model_name)

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gpt2 = gpt2.to(device)

def generate_text(prompt, max_new_tokens=50, style="neutral", temperature=0.7):
    # Add stylistic prefix
    if style == "casual":
        prompt = f"Yo dude, {prompt}"
    elif style == "formal":
        prompt = f"In conclusion, {prompt}"

    # Tokenize input
    inputs = tokenizer.encode(prompt, return_tensors="pt").to(device)

    # Generate text
    outputs = gpt2.generate(
        inputs,
        max_length=inputs.shape[1] + max_new_tokens,
        temperature=temperature,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id
    )

    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return result[len(prompt):].strip()

def clean_to_complete_sentence(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences[0] if sentences else text

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_input = data.get('text', '')
    style = data.get('style', 'neutral')
    max_tokens = int(data.get('max_tokens', 50))
    
    if user_input:
        raw_output = generate_text(user_input, style=style, max_new_tokens=max_tokens)
        final_output = clean_to_complete_sentence(raw_output)
        return jsonify({'result': final_output})
    return jsonify({'result': ''})

if __name__ == '__main__':
    app.run(debug=True)