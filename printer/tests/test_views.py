from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from printer.services.octoprint import (
    OctoPrintAuthenticationError,
    OctoPrintConflictError,
    OctoPrintConnectionError,
    OctoPrintResponseError,
    OctoPrintTimeoutError,
)


@pytest.fixture
def api_client():
    return APIClient()


@patch("printer.views.OctoPrintClient")
def test_printer_status_success(mock_client, api_client):
    expected_data = {
        "server": {"online": True},
        "connection": {
            "connected": True,
            "state": "Operational",
            "port": "/dev/ttyUSB0",
            "baudrate": 115200,
        },
        "printer": {
            "state": "Operational",
            "flags": {"operational": True},
        },
        "temperature": {
            "tool0": {"actual": 24.0, "target": 0.0},
            "bed": {"actual": 25.0, "target": 0.0},
        },
        "job": {
            "state": "Operational",
            "progress": {},
        },
    }

    mock_instance = mock_client.return_value
    mock_instance.get_dashboard_data.return_value = expected_data

    response = api_client.get("/api/printer/status/")

    assert response.status_code == 200
    assert response.json() == expected_data

    mock_instance.get_dashboard_data.assert_called_once()


def test_printer_status_service_error(api_client):
    with patch("printer.views.OctoPrintClient") as mock_client:
        mock_client.return_value.get_dashboard_data.side_effect = (
            OctoPrintTimeoutError("Timeout")
        )

        response = api_client.get("/api/printer/status/")

    assert response.status_code == 503
    assert response.data["error"]["code"] == "octoprint_timeout"


def test_printer_status_service_unavailable(api_client):
    with patch("printer.views.OctoPrintClient") as mock_client:
        mock_client.return_value.get_dashboard_data.side_effect = (
            OctoPrintConnectionError(
                "Não foi possível conectar ao OctoPrint."
            )
        )

        response = api_client.get("/api/printer/status/")

    assert response.status_code == 503
    assert response.data["error"]["code"] == "octoprint_connection_error"

@pytest.mark.parametrize(
    ("exception", "expected_status", "expected_code"),
    [
        (
            OctoPrintTimeoutError("Timeout"),
            503,
            "octoprint_timeout",
        ),
        (
            OctoPrintConnectionError("Connection error"),
            503,
            "octoprint_connection_error",
        ),
        (
            OctoPrintAuthenticationError("Authentication error"),
            502,
            "octoprint_authentication_error",
        ),
        (
            OctoPrintConflictError("Conflict"),
            502,
            "octoprint_conflict",
        ),
        (
            OctoPrintResponseError("Invalid response"),
            502,
            "octoprint_response_error",
        ),
    ],
)
def test_printer_status_error(
    api_client,
    exception,
    expected_status,
    expected_code,
):
    with patch("printer.views.OctoPrintClient") as mock_client:
        mock_client.return_value.get_dashboard_data.side_effect = exception

        response = api_client.get("/api/printer/status/")

    assert response.status_code == expected_status
    assert response.data["error"]["code"] == expected_code