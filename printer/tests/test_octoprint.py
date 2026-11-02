import requests
import pytest

from unittest.mock import Mock, patch

from printer.services.octoprint import (
    OctoPrintClient,
    OctoPrintError,
)


def test_client_initialization(settings):
    from printer.services.octoprint import OctoPrintClient

    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 10

    client = OctoPrintClient()

    assert client.base_url == "http://localhost:5000"
    assert client.api_key == "test-api-key"
    assert client.timeout == 10
    assert client.headers == {
        "X-Api-Key": "test-api-key"
    }

@patch("printer.services.octoprint.requests.get")
def test_get_success(mock_get, settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    mock_response = Mock()
    mock_response.json.return_value = {
        "api": "0.1",
        "server": "1.11.8",
        "text": "OctoPrint 1.11.8",
    }

    mock_get.return_value = mock_response

    client = OctoPrintClient()

    result = client._get("version")

    assert result["server"] == "1.11.8"
    assert result["api"] == "0.1"

    mock_get.assert_called_once_with(
        "http://localhost:5000/api/version",
        headers={"X-Api-Key": "test-api-key"},
        timeout=5,
    )