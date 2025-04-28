import React, { useState } from "react";
import "./DiabetesPrediction.css";

const DiabetesPrediction = () => {
  const [formData, setFormData] = useState({
    pregnancies: "",
    glucose: "",
    bloodPressure: "",
    skinThickness: "",
    insulin: "",
    bmi: "",
    diabetesPedigreeFunction: "",
    age: "",
  });

  const [prediction, setPrediction] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [submittedData, setSubmittedData] = useState(null);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const validateForm = () => {
    for (const key in formData) {
      if (formData[key] === "") {
        setError(`Please fill in the ${key} field.`);
        return false;
      }
    }
    setError("");
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!validateForm()) return;

    setLoading(true);
    setError("");

    const formattedData = {
      features: [
        parseFloat(formData.pregnancies),
        parseFloat(formData.glucose),
        parseFloat(formData.bloodPressure),
        parseFloat(formData.skinThickness),
        parseFloat(formData.insulin),
        parseFloat(formData.bmi),
        parseFloat(formData.diabetesPedigreeFunction),
        parseFloat(formData.age),
      ],
    };

    try {
      const response = await fetch("http://localhost:5000/predict", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formattedData),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch prediction");
      }

      const result = await response.json();
      setPrediction(result.prediction);
      setSubmittedData(formData); // Store submitted data
    } catch (error) {
      setError("Error connecting to the server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="prediction-container">
      <div className="prediction-card">
        <h1>Diabetes Prediction</h1>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            {Object.keys(formData).map((key) => (
              <div key={key} className="form-group">
                <label>{key}:</label>
                <input
                  type="number"
                  name={key}
                  value={formData[key]}
                  onChange={handleChange}
                  required
                />
              </div>
            ))}
          </div>
          <button type="submit" disabled={loading}>
            {loading ? "Predicting..." : "Get Prediction"}
          </button>
        </form>
        {error && <p className="error-message">{error}</p>}
        {submittedData && (
          <div className="submitted-data">
            <h2>Submitted Data</h2>
            <div className="data-grid">
              {Object.keys(submittedData).map((key) => (
                <div key={key} className="data-item">
                  <span className="data-label">{key}:</span>
                  <span className="data-value">{submittedData[key]}</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {prediction && (
          <div className="prediction-result">
            <h2>Prediction Result</h2>
            <p className={prediction === "Diabetic" ? "diabetic" : "non-diabetic"}>
              {prediction}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default DiabetesPrediction;