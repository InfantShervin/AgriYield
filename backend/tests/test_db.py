import pytest
from backend.db import save_prediction, PredictionRecord, SessionLocal
from datetime import datetime
from unittest.mock import MagicMock, patch

def test_save_prediction_success(mocker):
    """Verify that save_prediction correctly interacts with SQLAlchemy session"""
    # ⚡ Mock the session
    mock_session = MagicMock()
    mocker.patch("backend.db.SessionLocal", return_value=mock_session)
    # ⚡ Mock the engine to ensure it "exists" for the check
    mocker.patch("backend.db.engine", True)

    data = {
        "temperature": 25.0,
        "humidity": 60.0,
        "precipitation": 100.0,
        "soil_ph": 6.8,
        "latitude": 12.34,
        "longitude": 56.78,
        "crop_type": "wheat",
        "predicted_yield": 4.5
    }

    result = save_prediction(data)

    assert result is True
    # Verify that add, commit, refresh, and close were called
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()
    mock_session.close.assert_called_once()

def test_save_prediction_no_engine():
    """Verify that it returns False if engine is None (DB connection failed)"""
    with patch("backend.db.engine", None):
        result = save_prediction({})
        assert result is False

def test_save_prediction_exception(mocker):
    """Verify that it handles exceptions during DB commit"""
    mock_session = MagicMock()
    mock_session.commit.side_effect = Exception("DB Error")
    mocker.patch("backend.db.SessionLocal", return_value=mock_session)
    mocker.patch("backend.db.engine", True)

    result = save_prediction({"temperature": 25.0})
    assert result is False
    mock_session.close.assert_called_once()
