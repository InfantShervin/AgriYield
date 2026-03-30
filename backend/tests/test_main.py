import pytest
from fastapi.testclient import TestClient
from backend.main import app
import numpy as np

client = TestClient(app)

def test_health_check_api():
    """Verify that the base endpoint is responsive"""
    response = client.get("/")
    assert response.status_code == 200
    assert "AgriYield AI ML Backend is Running!" in response.json()["message"]

def test_prediction_api_success(mocker):
    """
    Verify the prediction flow with dependencies mocked out.
    - Mocks the database save to ensure no real network is required
    - Mocks the model prediction so we don't have to load the .pkl file
    """
    # ⚡ Step 1: Mock the DB save function in db.py
    mock_save = mocker.patch("backend.db.save_prediction", return_value=True)
    
    # ⚡ Step 2: Mock the preprocessor and model in main.py
    # We mock the return value so the test is instant
    mocker.patch("backend.main.processor.preprocess_request", 
                 return_value=np.zeros((1, 8)))
    mocker.patch("backend.main.ensemble_model.predict", 
                 return_value=np.array([3.12]))

    # Execute the request
    payload = {
        "temperature": 28.5,
        "humidity": 70.0,
        "precipitation": 120.0,
        "soil_ph": 6.5,
        "soil_nutrients": 140.0,
        "latitude": 20.5,
        "longitude": 78.5,
        "crop_type": "rice"
    }
    
    response = client.post("/api/predict", json=payload)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["predicted_yield"] == 3.12 # Should match our mocked value
    
    # Verify that the database function was actually called with the data
    mock_save.assert_called_once()

def test_prediction_api_invalid_input():
    """Verify that the API rejects missing fields with 422 Unprocessable Entity"""
    payload = {
        "temperature": 28.5 # Missing all other fields
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 422
