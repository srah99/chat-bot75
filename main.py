import os
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

text_generator = pipeline('text-generation', model='Salesforce/code-t5-small')

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
parameters = {
    "max_length": 128,
    "num_return_sequences": 5,
    "top_p": 0.9,
    "top_k": 50,
    "temperature": 0.7,
    "repetition_penalty": 1.5  # added repetition penalty
}
    response = text_generator(user_input, **parameters)
    sentences = [r['generated_text'] for r in response]
    unique_sentences = list(dict.fromkeys(sentences))
    truncated_response = '. '.join(unique_sentences[:5])
    return jsonify({"response": truncated_response})
    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
