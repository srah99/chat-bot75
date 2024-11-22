import os
from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

text_generator = pipeline('text-generation')

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
    parameters = {
        "max_length": 256,
        "num_return_sequences": 1,
        "top_p": 0.9,
        "top_k": 50,
        "temperature": 0.5
    }
    response = text_generator(user_input, **parameters)
    sentences = response[0]['generated_text'].split('. ')
    unique_sentences = list(dict.fromkeys(sentences))  # remove duplicates
    truncated_response = '. '.join(unique_sentences[:5])  # limit to 5 sentences
    return jsonify({"response": truncated_response})
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
