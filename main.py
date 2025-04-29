print("Chatbot initialized successfuly")
import os
import requests
import socket
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

app = Flask(__name__, static_folder='static', static_url_path='')
# app.debug = True

@app.route('/')
def serve_html():
    return send_from_directory(app.static_folder, 'index.html')

# Load environment variables
load_dotenv()

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def query_model(prompt):
    api_key = os.environ.get('MY_API')
    # Check if API key is missing or empty
    if not api_key:
        print("API key (MY_API) not found in environment variables. Returning mock response.")
        # Mimic the expected successful response structure
        return {"choices": [{"text": f"This is a mock response because the API key is missing. Your input was: 	'{prompt}'"}]}

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 250,
            "temperature": 0.7,
            "top_p": 0.9
        }
    }
    try:
        print(f"Attempting API call to {API_URL}...")
        response = requests.post(API_URL, headers=headers, json=payload)
        print(f"API response status code: {response.status_code}")
        # Check specifically for authentication error
        if response.status_code == 401:
             print("API key is invalid (401 Unauthorized). Returning mock response.")
             # Return mock response but indicate the key was invalid
             return {"choices": [{"text": f"This is a mock response because the provided API key is invalid. Your input was: 	'{prompt}'"}]}
        # Raise exceptions for other bad status codes (4xx client error or 5xx server error)
        response.raise_for_status()
        # If successful, return the JSON response
        print("API call successful.")
        return response.json()
    except requests.exceptions.RequestException as e:
        # Catch any request exceptions (connection, timeout, etc.) or errors raised by raise_for_status()
        print(f"API request failed: {e}. Returning mock response.")
        # Return mock response indicating an API error
        return {"choices": [{"text": f"This is a mock response due to an API error ({type(e).__name__}). Your input was: 	'{prompt}'"}]}

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
    app.run(debug=False, host="0.0.0.0", port=port)

