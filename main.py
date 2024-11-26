import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

MODEL_ID = "tiiuae/falcon-7b-instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def query_model(prompt):
    headers = {"Authorization": f"Bearer {os.environ.get('MY_API')}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
    response = query_model(user_input)
    if "error" in response:
        return jsonify({"error": response["error"]}), 500
    return jsonify({"response": response[0]["generated_text"]})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
