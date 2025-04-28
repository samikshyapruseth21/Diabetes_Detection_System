import React from "react";
import DiabetesPrediction from "./components/DiabetesPrediction";
import Chatbot from "./components/Chatbot";
import "./App.css";

const App = () => {
  return (
    <div className="container">
      <DiabetesPrediction />
      <Chatbot />
    </div>
  );
};

export default App;