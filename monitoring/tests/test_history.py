import pytest

from monitoring.models import (
    PrinterStateHistory,
    TemperatureHistory,
)
from monitoring.services.history import (
    save_printer_state_history,
    save_temperature_history,
)


@pytest.mark.django_db
def test_save_temperature_history():
    temperature_data = {
        "tool": {"actual": 200.0, "target": 210.0},
        "bed": {"actual": 60.0, "target": 65.0},
    }

    history = save_temperature_history(temperature_data)

    assert isinstance(history, TemperatureHistory)
    assert history.nozzle_actual == 200.0
    assert history.nozzle_target == 210.0
    assert history.bed_actual == 60.0
    assert history.bed_target == 65.0


@pytest.mark.django_db
def test_save_temperature_history_with_incomplete_data():
    temperature_data = {
        "tool": {"actual": 200.0},
        "bed": {"actual": 60.0, "target": 65.0},
    }

    history = save_temperature_history(temperature_data)

    assert history is None
    assert TemperatureHistory.objects.count() == 0




@pytest.mark.django_db
def test_save_printer_state_history():
    state_data = {
        "state": "Printing",
        "flags": {
            "operational": True,
            "printing": True,
            "paused": False,
            "error": False,
        },
    }

    history = save_printer_state_history(state_data)

    assert isinstance(history, PrinterStateHistory)
    assert history.state == "Printing"
    assert history.flags["printing"] is True
    assert PrinterStateHistory.objects.count() == 1


@pytest.mark.django_db
def test_save_printer_state_history_without_state():
    state_data = {
        "state": None,
        "flags": {},
    }

    history = save_printer_state_history(state_data)

    assert history is None
    assert PrinterStateHistory.objects.count() == 0


@pytest.mark.django_db
def test_save_printer_state_history_without_flags():
    state_data = {
        "state": "Operational",
    }

    history = save_printer_state_history(state_data)

    assert history is not None
    assert history.flags == {}