import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_TOKEN = "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"
MODEL_ID = "Salesforce/code-t5-small"
API_URL = f"https://api-inference.huggingface.co/models/{chat-bot75}"

def query_model(prompt):
    headers = {"Authorization": f"Bearer {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}"}
    payload = {"inputs": prompt}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
    response = query_model(user_input)
    return jsonify({"response": response['generated_text']})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
