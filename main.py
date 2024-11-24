import os
from flask import Flask, request, jsonify
from transformers import AutoModelForCausalLM, AutoTokenizer, GenerationConfig

app = Flask(__name__)

model_name = 'Salesforce/code-t5-small'
model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

generation_config = GenerationConfig(
    max_length=128,
    num_beams=10,  # increased num_beams for more diverse text
    no_repeat_ngram_size=2  # added to reduce repetition
)

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
    input_ids = tokenizer.encode(user_input, return_tensors='pt')
    output = model.generate(input_ids, **generation_config)
    sentences = tokenizer.batch_decode(output, skip_special_tokens=True)
    response_text = ' '.join([' '.join(sentence.split()) for sentence in sentences])
    unique_words = list(dict.fromkeys(response_text.split()))
    truncated_response = ' '.join(unique_words[:50])  # limit to 50 words
    return jsonify({"response": truncated_response})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
