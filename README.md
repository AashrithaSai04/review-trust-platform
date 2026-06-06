# Review Trust Platform

## Overview

Review Trust Platform is an AI-powered web application designed to identify and analyze untrustworthy product and service reviews. The platform leverages Machine Learning and Natural Language Processing (NLP) techniques to classify reviews, provide prediction explanations, and assist with content moderation. It combines a React-based frontend with a Python-powered backend to deliver an interactive and scalable review analysis system.

---

## Features

### Review Classification

* Predicts whether a review is trustworthy or untrustworthy.
* Uses machine learning models trained on review datasets.

### Explainable AI (XAI)

* Provides explanations for model predictions.
* Enhances transparency and interpretability of classification results.

### Review Moderation

* Identifies suspicious reviews for further inspection.
* Supports moderation workflows for content management.

### Dataset Upload and Evaluation

* Upload datasets for analysis and model testing.
* View evaluation metrics and model performance reports.

### Responsive Web Interface

* User-friendly React frontend.
* Real-time communication with backend APIs.

---

## Tech Stack

### Frontend

* React.js
* HTML
* CSS
* JavaScript

### Backend

* Python
* FastAPI

### Machine Learning

* NLP
* Scikit-learn
* Transformers
* Explainable AI Techniques (SHAP/XAI)

### Database

* MongoDB

---

## System Architecture

```text
Frontend (React.js)
        |
        v
Backend API (FastAPI)
        |
        v
Machine Learning Models
        |
        v
MongoDB Database
```

The frontend interacts with FastAPI endpoints for review classification, explanation generation, moderation, and data management. Machine learning models process review text and return predictions with supporting insights.

---

## Project Structure

```text
Review-Trust-Platform/
│
├── frontend/                 # React frontend
├── ml-service/               # FastAPI backend
├── ml-pipeline/              # Training and evaluation scripts
├── my_model/                 # Saved model artifacts
├── data/                     # Datasets
├── README.md
└── requirements.txt
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/AashrithaSai04/review-trust-platform.git
cd review-trust-platform
```

### Backend Setup

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r ml-service/requirements.txt
```

### Frontend Setup

```bash
cd frontend
npm install
```

---

## Running the Application

### Start Backend

```bash
cd ml-service

uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend

```bash
cd frontend

npm run dev
```

Frontend will be available at:

```text
http://localhost:5173
```

Backend API will run at:

```text
http://localhost:8000
```

---

## API Endpoints

### Predict Review

```http
POST /predict
```

Request:

```json
{
  "review": "This product exceeded my expectations."
}
```

Response:

```json
{
  "label": "trustworthy",
  "score": 0.95
}
```

### Explain Prediction

```http
POST /explain
```

Returns model explanation and feature importance information.

### Upload Dataset

```http
POST /upload
```

Uploads review datasets for analysis and evaluation.

### Moderation

```http
POST /moderation
```

Flags suspicious reviews for review and moderation.

---

## Machine Learning Pipeline

The platform follows a complete ML workflow:

1. Data Collection
2. Data Cleaning and Preprocessing
3. Text Vectorization
4. Model Training
5. Model Evaluation
6. Prediction and Explainability
7. Deployment through FastAPI

---

## Key Highlights

* AI-powered review trust classification
* NLP-based text processing
* Explainable AI integration
* FastAPI backend services
* React-based responsive frontend
* Scalable architecture for review moderation

---
