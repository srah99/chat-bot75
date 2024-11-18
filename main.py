from flask import Flask, request, jsonify
from google.cloud import storage
import vertexai
from vertexai.language_models import TextGenerationModel

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to the AI Chatbot Web App!"

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['input']
    
    # Initialize Vertex AI
    vertexai.init(project="your-project-id", location="us-central1")
    parameters = {
        "temperature": 0.2,
        "max_output_tokens": 256,
        "top_p": 0.8,
        "top_k": 40
    }
    model = TextGenerationModel.from_pretrained("text-bison@001")
    response = model.predict(
        user_input,
        **parameters
    )
    return jsonify({"response": response.text})

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

