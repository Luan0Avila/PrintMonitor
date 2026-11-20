
from decimal import Decimal

import pytest

from monitoring.models import PrinterStateHistory, PrintJobHistory, TemperatureHistory
from monitoring.services.history import (
    save_print_job_history,
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

@pytest.mark.django_db
def test_save_print_job_history():
    job_data = {
        "file": "modelo.stl",
        "state": "Printing",
        "progress": 25.5,
        "print_time": 120,
        "print_time_left": 300,
    }

    history = save_print_job_history(job_data)

    assert isinstance(history, PrintJobHistory)
    assert history.file_name == "modelo.stl"
    assert history.state == "Printing"
    assert history.progress == Decimal("25.50")
    assert history.print_time == 120
    assert history.print_time_left == 300
    assert history.started_at is not None
    assert history.completed_at is None


@pytest.mark.django_db
def test_update_existing_print_job_history():
    job_data = {
        "file": "modelo.stl",
        "state": "Printing",
        "progress": 25.5,
        "print_time": 120,
        "print_time_left": 300,
    }

    first_history = save_print_job_history(job_data)

    job_data["progress"] = 50.0
    job_data["print_time"] = 240
    job_data["print_time_left"] = 180

    updated_history = save_print_job_history(job_data)

    assert updated_history.pk == first_history.pk
    assert updated_history.progress == Decimal("50.00")
    assert updated_history.print_time == 240
    assert updated_history.print_time_left == 180
    assert PrintJobHistory.objects.count() == 1


@pytest.mark.django_db
def test_finish_existing_print_job_history():
    job_data = {
        "file": "modelo.stl",
        "state": "Printing",
        "progress": 99.0,
        "print_time": 500,
        "print_time_left": 5,
    }

    history = save_print_job_history(job_data)

    job_data["state"] = "Operational"
    job_data["progress"] = 100.0
    job_data["print_time_left"] = 0

    finished_history = save_print_job_history(job_data)

    assert finished_history.pk == history.pk
    assert finished_history.state == "Operational"
    assert finished_history.progress == Decimal("100.00")
    assert finished_history.completed_at is not None
    assert PrintJobHistory.objects.count() == 1


@pytest.mark.django_db
def test_save_print_job_history_without_file():
    job_data = {
        "file": None,
        "state": "Printing",
        "progress": 10.0,
    }

    history = save_print_job_history(job_data)

    assert history is None
    assert PrintJobHistory.objects.count() == 0
