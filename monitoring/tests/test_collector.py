from unittest.mock import patch

import pytest

from monitoring.services.collector import collect_printer_data
from printer.services.octoprint import OctoPrintTimeoutError


@pytest.fixture
def connected_dashboard_data():
    return {
        "server": {"online": True},
        "connection": {
            "connected": True,
            "state": "Printing",
            "port": "/dev/ttyUSB0",
            "baudrate": 115200,
        },
        "printer": {
            "state": "Printing",
            "flags": {
                "operational": True,
                "printing": True,
                "paused": False,
                "error": False,
            },
        },
        "temperature": {
            "tool": {"actual": 200.0, "target": 210.0},
            "bed": {"actual": 60.0, "target": 65.0},
        },
        "job": {
            "file": "modelo.stl",
            "state": "Printing",
            "progress": 45.0,
            "print_time": 120,
            "print_time_left": 150,
        },
    }


@pytest.mark.django_db
def test_collect_printer_data_success(connected_dashboard_data):
    with (
        patch("monitoring.services.collector.OctoPrintClient") as client_mock,
        patch(
            "monitoring.services.collector.save_temperature_history"
        ) as temperature_mock,
        patch("monitoring.services.collector.save_printer_state_history") as state_mock,
        patch("monitoring.services.collector.save_print_job_history") as job_mock,
    ):
        client_mock.return_value.get_dashboard_data.return_value = (
            connected_dashboard_data
        )

        result = collect_printer_data()

    assert result == connected_dashboard_data

    temperature_mock.assert_called_once_with(connected_dashboard_data["temperature"])

    state_mock.assert_called_once_with(connected_dashboard_data["printer"])

    job_mock.assert_called_once_with(connected_dashboard_data["job"])


@pytest.mark.django_db
def test_collect_printer_data_disconnected():
    disconnected_data = {
        "server": {"online": True},
        "connection": {
            "connected": False,
            "state": "Closed",
        },
        "printer": {
            "state": "Disconnected",
            "flags": {},
        },
        "temperature": {},
        "job": None,
    }

    with (
        patch("monitoring.services.collector.OctoPrintClient") as client_mock,
        patch(
            "monitoring.services.collector.save_temperature_history"
        ) as temperature_mock,
        patch("monitoring.services.collector.save_printer_state_history") as state_mock,
        patch("monitoring.services.collector.save_print_job_history") as job_mock,
    ):
        client_mock.return_value.get_dashboard_data.return_value = disconnected_data

        result = collect_printer_data()

    assert result == disconnected_data

    temperature_mock.assert_not_called()
    state_mock.assert_not_called()
    job_mock.assert_not_called()


def test_collect_printer_data_without_job(connected_dashboard_data):
    connected_dashboard_data["job"] = None

    with (
        patch("monitoring.services.collector.OctoPrintClient") as client_mock,
        patch(
            "monitoring.services.collector.save_temperature_history"
        ) as temperature_mock,
        patch("monitoring.services.collector.save_printer_state_history") as state_mock,
        patch("monitoring.services.collector.save_print_job_history") as job_mock,
    ):
        client_mock.return_value.get_dashboard_data.return_value = (
            connected_dashboard_data
        )

        result = collect_printer_data()

    assert result == connected_dashboard_data

    temperature_mock.assert_called_once()
    state_mock.assert_called_once()
    job_mock.assert_not_called()


def test_collect_printer_data_propagates_timeout():
    with patch("monitoring.services.collector.OctoPrintClient") as client_mock:
        client_mock.return_value.get_dashboard_data.side_effect = OctoPrintTimeoutError(
            "Timeout"
        )

        with pytest.raises(OctoPrintTimeoutError):
            collect_printer_data()
