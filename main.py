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
        "temperature": 0.5,
        "truncation": True,  # added truncation parameter
        "return_full_text": False  # ensure only truncated text is returned
    }
    response = text_generator(user_input, **parameters)
    # truncate response further to 100 characters if needed
    truncated_response = response[0]['generated_text'][:100]
    return jsonify({"response": truncated_response})
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
