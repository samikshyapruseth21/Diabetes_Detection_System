import os
import pickle
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["diabetes_db"]
collection = db["predictions"]

# Load trained model
MODEL_PATH = os.getenv("MODEL_PATH", "backend/model/diabetes_model.pkl")
try:
    with open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)
except Exception as e:
    print(f"Error loading model: {e}")
    model = None

# Helper function to validate input data
def validate_input(data):
    required_keys = ["pregnancies", "glucose", "bloodPressure", "skinThickness", "insulin", "bmi", "diabetesPedigreeFunction", "age"]
    if not all(key in data for key in required_keys):
        return False, "Missing one or more required fields"
    try:
        features = [float(data[key]) for key in required_keys]
        return True, features
    except ValueError:
        return False, "Invalid data type in input fields"

# API Endpoint: Predict Diabetes
@app.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500

    data = request.get_json()
    is_valid, validation_result = validate_input(data)

    if not is_valid:
        return jsonify({"error": validation_result}), 400

    features = np.array(validation_result).reshape(1, -1)
    try:
        prediction = model.predict(features)[0]
        result = "Diabetic" if prediction == 1 else "Non-Diabetic"

        # Store result in MongoDB
        collection.insert_one({"input": data, "prediction": result})

        return jsonify({"prediction": result})
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": "An error occurred during prediction"}), 500

# API Endpoint: Get past predictions
@app.route("/history", methods=["GET"])
def get_history():
    try:
        history = list(collection.find({}, {"_id": 0}))
        return jsonify(history)
    except Exception as e:
        print(f"Error fetching history: {e}")
        return jsonify({"error": "An error occurred while fetching history"}), 500

if __name__ == "__main__":
    app.run(debug=True)