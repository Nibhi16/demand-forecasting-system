# HybridDemand AI: Real-Time Forecasting & Allocation System

A full-stack machine learning system that predicts demand and makes real-time resource allocation decisions, designed to simulate how modern data-driven systems operate in production environments.

---

## 🌐 Live Demo

- Dashboard: https://demand-forecasting-system-xkfwyws6pker6laf6ji8zh.streamlit.app/
- API Docs: https://demand-api-bsbz.onrender.com/docs

---

## 🧠 Overview

This project started as a demand forecasting problem but evolved into a complete system that goes beyond prediction.

Instead of just building a model, the goal was to design something closer to a real-world pipeline:
- Data flows continuously (simulated via streaming)
- Predictions are generated in real time
- Decisions are made automatically
- Results are visualized interactively

The focus was not just accuracy, but building something that resembles how real systems operate end-to-end.

---

## ⚙️ System Architecture

User (Dashboard)  
↓  
Streamlit UI  
↓  
FastAPI Backend (Render)  
↓  
XGBoost Model  
↓  
Allocation Engine  
↓  
Decision Output  

Kafka is used to simulate streaming data for real-time processing.

---

## 🚀 Features

- Real-time demand prediction using machine learning  
- Adaptive allocation system (Increase / Maintain / Reduce resources)  
- Interactive dashboard for monitoring and simulation  
- REST API for model inference  
- Kafka-based streaming pipeline (simulated real-time data)  
- Fully deployed system (frontend + backend)  

---

## 🧪 Model Details

- Models used:
  - Random Forest (baseline)
  - XGBoost (final model)

- Evaluation metrics:
  - RMSE (Root Mean Squared Error)
  - MAE (Mean Absolute Error)

XGBoost was selected as the final model due to better generalization and performance.

---

## 🧠 Key Insight

Demand is strongly influenced by historical patterns.

Lag-based features (previous demand values) played a significant role in improving prediction accuracy, reinforcing the time-series nature of the problem even within a machine learning setup.

---

## 🏗️ Tech Stack

- Backend: FastAPI  
- Frontend: Streamlit  
- Machine Learning: Scikit-learn, XGBoost  
- Streaming: Apache Kafka  
- Deployment: Render (API), Streamlit Cloud (Dashboard)  
- Other Tools: Pandas, NumPy, Joblib  

---

## ▶️ Running Locally

```bash
git clone https://github.com/Nibhi16/demand-forecasting-system
cd demand-forecasting-system

# create virtual environment
python -m venv venv
venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# run API
python -m uvicorn backend.app:app --reload

# run dashboard
streamlit run dashboard/app.py
📌 Notes
The trained model is included for deployment purposes
Kafka pipeline is used for simulation and demonstration
The system is modular and can be extended with real data sources
🎯 What This Project Demonstrates
Building end-to-end ML systems (not just models)
Integrating ML with APIs and real-time pipelines
Deploying production-like systems with live interfaces
Bridging the gap between data science and software engineering
📬 Contact
GitHub: https://github.com/Nibhi16
LinkedIn: https://linkedin.com/in/nibhigarg
⭐ Final Thought

This project reflects an effort to move beyond isolated models and toward building systems that can actually function in real-world scenarios.
