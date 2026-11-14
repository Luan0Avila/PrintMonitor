
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from monitoring.models import (
    PrinterStateHistory,
    PrintJobHistory,
    TemperatureHistory,
)


@pytest.mark.django_db
def test_create_temperature_history():
    history = TemperatureHistory.objects.create(
        nozzle_actual=200.0,
        nozzle_target=210.0,
        bed_actual=60.0,
        bed_target=65.0,
    )

    assert history.pk is not None
    assert history.nozzle_actual == 200.0
    assert history.nozzle_target == 210.0
    assert history.bed_actual == 60.0
    assert history.bed_target == 65.0
    assert history.recorded_at is not None


@pytest.mark.django_db
def test_create_printer_state_history():
    history = PrinterStateHistory.objects.create(
        state="Printing",
    )

    assert history.pk is not None
    assert history.state == "Printing"
    assert history.flags == {}
    assert history.recorded_at is not None


@pytest.mark.django_db
def test_create_print_job_history():
    job = PrintJobHistory.objects.create(
        file_name="modelo.stl",
        state="Printing",
        progress=Decimal("45.50"),
        print_time=120,
        print_time_left=150,
    )

    assert job.pk is not None
    assert job.file_name == "modelo.stl"
    assert job.state == "Printing"
    assert job.progress == Decimal("45.50")
    assert job.print_time == 120
    assert job.print_time_left == 150


def test_print_job_progress_cannot_exceed_100():
    job = PrintJobHistory(
        file_name="modelo.stl",
        state="Printing",
        progress=Decimal("101.00"),
    )

    with pytest.raises(ValidationError):
        job.full_clean()


def test_print_job_progress_cannot_be_negative():
    job = PrintJobHistory(
        file_name="modelo.stl",
        state="Printing",
        progress=Decimal("-1.00"),
    )

    with pytest.raises(ValidationError):
        job.full_clean()
