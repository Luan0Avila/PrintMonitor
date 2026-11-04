from unittest.mock import Mock, patch

import pytest
import requests

from printer.services.octoprint import (
    OctoPrintAuthenticationError,
    OctoPrintClient,
    OctoPrintConflictError,
    OctoPrintConnectionError,
    OctoPrintError,
    OctoPrintResponseError,
    OctoPrintTimeoutError,
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
    assert client.headers == {"X-Api-Key": "test-api-key"}


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


@patch("printer.services.octoprint.requests.get")
def test_get_timeout(mock_get, settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    mock_get.side_effect = requests.Timeout

    client = OctoPrintClient()

    with pytest.raises(OctoPrintTimeoutError):
        client._get("version")


@patch("printer.services.octoprint.requests.get")
def test_get_connection_error(mock_get, settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    mock_get.side_effect = requests.ConnectionError

    client = OctoPrintClient()

    with pytest.raises(OctoPrintConnectionError):
        client._get("version")


@pytest.mark.parametrize(
    ("status_code", "expected_exception"),
    [
        (403, OctoPrintAuthenticationError),
        (409, OctoPrintConflictError),
        (500, OctoPrintResponseError),
    ],
)
@patch("printer.services.octoprint.requests.get")
def test_get_http_error(
    mock_get,
    status_code,
    expected_exception,
    settings,
):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    mock_response = Mock()
    mock_response.status_code = status_code

    mock_get.return_value = mock_response
    mock_response.raise_for_status.side_effect = requests.HTTPError(
        response=mock_response
    )

    client = OctoPrintClient()

    with pytest.raises(expected_exception):
        client._get("version")


def test_get_printer_status(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    expected = {"state": {"text": "Operational"}}
    client._get = Mock(return_value=expected)

    result = client.get_printer_status()

    assert result == expected
    client._get.assert_called_once_with("printer")


def test_get_current_job(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    expected = {"state": "Operational", "progress": {}}
    client._get = Mock(return_value=expected)

    result = client.get_current_job()

    assert result == expected
    client._get.assert_called_once_with("job")


def test_get_temperature(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    expected = {
        "tool0": {"actual": 24.0, "target": 0.0},
        "bed": {"actual": 25.0, "target": 0.0},
    }

    client.get_printer_status = Mock(return_value={"temperature": expected})

    result = client.get_temperature()

    assert result == expected
    client.get_printer_status.assert_called_once()


def test_get_connection(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    expected = {
        "current": {
            "state": "Operational",
            "port": "/dev/ttyUSB0",
        }
    }

    client._get = Mock(return_value=expected)

    result = client.get_connection()

    assert result == expected
    client._get.assert_called_once_with("connection")


def test_get_dashboard_data_operational(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    client.get_connection = Mock(
        return_value={
            "current": {
                "state": "Operational",
                "port": "/dev/ttyUSB0",
                "baudrate": 115200,
            }
        }
    )

    client.get_printer_status = Mock(
        return_value={
            "state": {
                "text": "Operational",
                "flags": {"operational": True},
            },
            "temperature": {
                "tool0": {"actual": 24.0, "target": 0.0},
                "bed": {"actual": 25.0, "target": 0.0},
            },
        }
    )

    client.get_current_job = Mock(
        return_value={
            "state": "Operational",
            "progress": {},
        }
    )

    result = client.get_dashboard_data()

    assert result["server"]["online"] is True
    assert result["connection"]["connected"] is True
    assert result["printer"]["state"] == "Operational"
    assert "tool0" in result["temperature"]
    assert result["job"]["state"] == "Operational"

    client.get_printer_status.assert_called_once()
    client.get_current_job.assert_called_once()


def test_get_dashboard_data_disconnected(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    client.get_connection = Mock(
        return_value={
            "current": {
                "state": "Closed",
                "port": "/dev/ttyUSB0",
                "baudrate": 115200,
            }
        }
    )

    client.get_printer_status = Mock()
    client.get_current_job = Mock()

    result = client.get_dashboard_data()

    assert result["server"]["online"] is True
    assert result["connection"]["connected"] is False
    assert result["printer"]["state"] == "Disconnected"
    assert result["temperature"] == {}
    assert result["job"] is None

    client.get_printer_status.assert_not_called()
    client.get_current_job.assert_not_called()


@patch("printer.services.octoprint.requests.get")
def test_get_request_exception(mock_get, settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    mock_get.side_effect = requests.RequestException("Erro inesperado na requisição")

    client = OctoPrintClient()

    with pytest.raises(OctoPrintError) as error:
        client._get("version")

    assert "Erro na requisição" in str(error.value)
    assert "Erro inesperado na requisição" in str(error.value)

def test_get_dashboard_data_printing(settings):
    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 5

    client = OctoPrintClient()

    client.get_connection = Mock(return_value={
        "current": {
            "state": "Printing",
            "port": "/dev/ttyUSB0",
            "baudrate": 115200,
        }
    })

    client.get_printer_status = Mock(return_value={
        "state": {
            "text": "Printing",
            "flags": {"printing": True},
        },
        "temperature": {},
    })

    client.get_current_job = Mock(return_value={
        "state": "Printing",
        "progress": {},
    })

    result = client.get_dashboard_data()

    assert result["connection"]["connected"] is True
    assert result["printer"]["state"] == "Printing"

    client.get_printer_status.assert_called_once()
    client.get_current_job.assert_called_once()