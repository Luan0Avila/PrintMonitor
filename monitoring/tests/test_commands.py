from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from printer.services.octoprint import OctoPrintTimeoutError


@pytest.fixture
def connected_data():
    return {
        "server": {"online": True},
        "connection": {
            "connected": True,
            "state": "Operational",
        },
        "printer": {
            "state": "Operational",
            "flags": {"operational": True},
        },
        "temperature": {},
        "job": {
            "file": "modelo.stl",
            "state": "Operational",
            "progress": 100,
        },
    }


@pytest.mark.django_db
def test_collect_printer_data_command_success(connected_data):
    output = StringIO()

    with patch(
        "monitoring.management.commands.collect_printer_data.collect_printer_data",
        return_value=connected_data,
    ) as collector:
        call_command("collect_printer_data", stdout=output)

    collector.assert_called_once()

    assert "Coleta realizada" in output.getvalue()
    assert "modelo.stl" in output.getvalue()


@pytest.mark.django_db
def test_collect_printer_data_command_disconnected():
    disconnected_data = {
        "server": {"online": True},
        "connection": {
            "connected": False,
            "state": "Closed",
        },
    }

    output = StringIO()

    with patch(
        "monitoring.management.commands.collect_printer_data.collect_printer_data",
        return_value=disconnected_data,
    ):
        call_command("collect_printer_data", stdout=output)

    assert "impressora desconectada" in output.getvalue()


def test_collect_printer_data_command_timeout():
    with patch(
        "monitoring.management.commands.collect_printer_data.collect_printer_data",
        side_effect=OctoPrintTimeoutError("Timeout"),
    ):
        with pytest.raises(CommandError):
            call_command("collect_printer_data")
