print("Chatbot initialized successfuly")
import os
import requests
import socket
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static', static_url_path='')
app.debug = True

@app.route('/')
def serve_html():
    return send_from_directory(app.static_folder, 'index.html')

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

@app.route('/chat', methods=['POST'])
def chat():
    try:
        print("Received chat request...")
        user_input = request.json['input']
        print("User input:", user_input)
        response = query_model(user_input)
        print("Model response:", response)
        if response is None:
            print("Model returned None")
            return jsonify({"error": "Model error"}), 500
        if "error" in response:
            print("Model error:", response["error"])
            return jsonify({"error": response["error"]}), 400
        if isinstance(response, dict) and "choices" in response:
            print("Successful response")
            return jsonify({"response": response["choices"][0]["text"]}), 200
        else:
            print("Invalid model response format")
            return jsonify({"error": "Invalid response format"}), 400
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({"error": str(e)}), 500
        
def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    port = find_free_port()
    print(f"Flask app running on port {port}")
    app.run(debug=True, host="0.0.0.0", port=port)

