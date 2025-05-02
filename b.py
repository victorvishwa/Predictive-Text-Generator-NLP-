import streamlit as st
from transformers import GPT2LMHeadModel, GPT2Tokenizer, MarianMTModel, MarianTokenizer
import torch
import re
from langdetect import detect  # Language detection using langdetect

# Load GPT-2 model and tokenizer
model_name = "gpt2"
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
gpt2 = GPT2LMHeadModel.from_pretrained(model_name)

# Load translation model
def load_translation_model(source_lang, target_lang):
    model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{target_lang}'
    model = MarianMTModel.from_pretrained(model_name)
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    return model, tokenizer

# Set device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
gpt2 = gpt2.to(device)

# Function to generate text
def generate_text(prompt, max_new_tokens=50, style="neutral", temperature=0.7):
    # Add stylistic prefix
    if style == "shakespeare":
        prompt = f"As thy wish: {prompt}"
    elif style == "casual":
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

# Clean output to complete the first sentence
def clean_to_complete_sentence(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return sentences[0] if sentences else text

# Translation helper functions
def translate_text(text, src_lang, tgt_lang):
    model, tokenizer = load_translation_model(src_lang, tgt_lang)
    inputs = tokenizer.encode(text, return_tensors="pt").to(device)
    translated = model.generate(inputs, max_length=512)
    translated_text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return translated_text

# Streamlit UI
st.title("Predictive Text Generator")

# Language selector
language = st.selectbox("Select Language", ["English", "Hindi", "Tamil", "Kannada"])

# Input prompt based on language selection
if language == "English":
    user_input = st.text_input("Enter your sentence...", value="I want to")
elif language == "Hindi":
    user_input = st.text_input("अपना वाक्य दर्ज करें...", value="मुझे तुम्हारी मदद चाहिए।")
elif language == "Tamil":
    user_input = st.text_input("உங்கள் வாக்கியத்தை உள்ளிடவும்...", value="எனக்கு உங்களுடைய உதவி வேண்டும்.")
elif language == "Kannada":
    user_input = st.text_input("ನಿಮ್ಮ ವಾಕ್ಯವನ್ನು ನಮೂದಿಸಿ...", value="ನನಗೆ ನಿಮ್ಮ ಸಹಾಯ ಬೇಕಾಗಿದೆ.")

# Style selector
style = st.selectbox("Choose style", ["neutral", "casual", "formal"])

# Max token slider
max_tokens = st.slider("Max tokens to generate", 10, 100, value=50)

if user_input:
    # Detect language and translate if needed
    detected_language = detect(user_input)  # Detect language with langdetect
    
    if detected_language != 'en':  # If input is not in English
        # Translate the input text to English
        user_input = translate_text(user_input, detected_language, 'en')
    
    # Generate and clean text
    raw_output = generate_text(user_input, style=style, max_new_tokens=max_tokens)
    final_output = clean_to_complete_sentence(raw_output)
    
    # Translate back to the original language
    if detected_language != 'en':  # If input was not in English
        final_output = translate_text(final_output, 'en', detected_language)

    # Display result
    st.markdown(f"**Predicted Text:** `{final_output}`")
