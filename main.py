import os
import requests
import socket
import logging # Added logging
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    filename='security.log',
    filemode='a',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = Flask(__name__, static_folder='static', static_url_path='')
# app.debug = True

@app.route('/')
def serve_html():
    # Log access to the root page
    logging.info(f"Root page accessed by {request.remote_addr}")
    return send_from_directory(app.static_folder, 'index.html')

# Load environment variables
load_dotenv()

MODEL_ID = "meta-llama/Meta-Llama-3.1-8B-Instruct"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

def query_model(prompt):
    # Log the query attempt
    logging.info(f"Query received from {request.remote_addr}: {prompt[:50]}...") # Log first 50 chars

    api_key = os.environ.get('MY_API')
    # Check if API key is missing or empty
    if not api_key:
        logging.warning(f"API key (MY_API) not found for request from {request.remote_addr}.")
        # Mimic the expected successful response structure
        return {"choices": [{"text": f"This is a mock response because the API key is missing. Your input was: \t'{prompt}'"}]}

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1024,
            "temperature": 0.7,
            "top_p": 0.9,
            "repetition_penalty": 1.2
        }
    }
    try:
        logging.info(f"Attempting API call to {API_URL} for {request.remote_addr}...")
        response = requests.post(API_URL, headers=headers, json=payload)
        logging.info(f"API response status code for {request.remote_addr}: {response.status_code}")
        # Check specifically for authentication error
        if response.status_code == 401:
             logging.error(f"Invalid API key (401 Unauthorized) used by {request.remote_addr}.")
             # Return mock response but indicate the key was invalid
             return {"choices": [{"text": f"This is a mock response because the provided API key is invalid. Your input was: \t'{prompt}'"}]}
        # Raise exceptions for other bad status codes (4xx client error or 5xx server error)
        response.raise_for_status()
        # If successful, return the JSON response
        logging.info(f"API call successful for {request.remote_addr}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        # Catch any request exceptions (connection, timeout, etc.) or errors raised by raise_for_status()
        logging.error(f"API request failed for {request.remote_addr}: {e}")
        # Return mock response indicating an API error
        return {"choices": [{"text": f"This is a mock response due to an API error ({type(e).__name__}). Your input was: \t'{prompt}'"}]}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        logging.info(f"Chat request received from {request.remote_addr}...")
        user_input = request.json['input']
        # Basic input validation/sanitization example (can be expanded)
        if len(user_input) > 2000: # Limit input length
             logging.warning(f"Input too long from {request.remote_addr}. Length: {len(user_input)}")
             return jsonify({"error": "Input is too long."}), 400
        # Add more checks here if needed (e.g., for malicious patterns)

        logging.info(f"User input from {request.remote_addr}: {user_input[:50]}...")
        response = query_model(user_input)
        # Log the raw model response for debugging/auditing if needed (might be verbose)
        # logging.debug(f"Model response for {request.remote_addr}: {response}")

        if response is None:
            logging.error(f"Model returned None for {request.remote_addr}. Input: {user_input[:50]}...")
            return jsonify({"error": "Model error"}), 500
        if "error" in response:
            logging.error(f"Model error for {request.remote_addr}: {response['error']}. Input: {user_input[:50]}...")
            return jsonify({"error": response['error']}), 400

        # Check response formats
        if isinstance(response, list) and len(response) > 0 and "generated_text" in response[0]:
            logging.info(f"Successful response (generated_text format) for {request.remote_addr}.")
            return jsonify({"response": response[0]["generated_text"]}), 200
        elif isinstance(response, dict) and "choices" in response and len(response["choices"]) > 0 and "text" in response["choices"][0]:
            logging.info(f"Successful response (choices format) for {request.remote_addr}.")
            return jsonify({"response": response["choices"][0]["text"]}), 200
        else:
            logging.error(f"Invalid model response format for {request.remote_addr}: {response}. Input: {user_input[:50]}...")
            return jsonify({"error": "Invalid response format from model"}), 400
    except Exception as e:
        logging.exception(f"Unexpected error in /chat endpoint for {request.remote_addr}: {e}") # Log full traceback
        return jsonify({"error": str(e)}), 500

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    port = find_free_port()
    print(f"Flask app running on port {port}")
    app.run(debug=False, host="0.0.0.0", port=port)

