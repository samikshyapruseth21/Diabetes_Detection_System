import os
import pickle
import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client["diabetes_db"]
collection = db["predictions"]

# Load dataset
DATA_PATH = r"E:/DDS/backend/data/diabetes.csv"
data = pd.read_csv(DATA_PATH)
X = data.drop(columns=["Outcome"])
y = data["Outcome"]

# Train Random Forest model
def train_model():
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"Model trained with accuracy: {acc * 100:.2f}%")
    
    # Save model
    model_path = "backend/model/diabetes_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)

# Train and save model if not already trained
MODEL_PATH = "backend/model/diabetes_model.pkl"
if not os.path.exists(MODEL_PATH):
    train_model()

# Load trained model
def load_model():
    with open(MODEL_PATH, "rb") as f:
        return pickle.load(f)
model = load_model()

# API Endpoint: Predict Diabetes
@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        features = np.array(data["features"]).reshape(1, -1)
        prediction = model.predict(features)[0]
        result = "Diabetic" if prediction == 1 else "Non-Diabetic"
        
        # Store in MongoDB
        collection.insert_one({"input": data["features"], "prediction": result})
        
        return jsonify({"prediction": result})
    except Exception as e:
        return jsonify({"error": str(e)})

# API Endpoint: Get past predictions
@app.route("/history", methods=["GET"])
def get_history():
    history = list(collection.find({}, {"_id": 0}))
    return jsonify(history)

if __name__ == "__main__":
    app.run(debug=True)

