from datetime import timedelta
from decimal import Decimal

import pytest
from django.utils import timezone
from rest_framework.test import APIClient

from monitoring.models import (
    PrinterStateHistory,
    PrintJobHistory,
    TemperatureHistory,
)
from monitoring.serializers import (
    PrinterStateHistorySerializer,
    PrintJobHistorySerializer,
    TemperatureHistorySerializer,
)


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def sample_records():
    now = timezone.now()
    temperatures = [
        TemperatureHistory.objects.create(
            nozzle_actual=200 + index,
            nozzle_target=210,
            bed_actual=60,
            bed_target=65,
        )
        for index in range(3)
    ]
    states = [
        PrinterStateHistory.objects.create(
            state=f"State {index}", flags={"ready": True}
        )
        for index in range(2)
    ]
    jobs = [
        PrintJobHistory.objects.create(
            file_name=f"model-{index}.gcode",
            state="Completed",
            progress=Decimal("100.00"),
        )
        for index in range(2)
    ]
    # Give the fixture deterministic timestamps for ordering and date filtering.
    for index, record in enumerate(temperatures):
        TemperatureHistory.objects.filter(pk=record.pk).update(
            recorded_at=now - timedelta(days=2 - index)
        )
    for index, record in enumerate(states):
        PrinterStateHistory.objects.filter(pk=record.pk).update(
            recorded_at=now - timedelta(days=1 - index)
        )
    for index, record in enumerate(jobs):
        PrintJobHistory.objects.filter(pk=record.pk).update(
            created_at=now - timedelta(days=1 - index)
        )
    return temperatures, states, jobs


@pytest.mark.django_db
def test_model_serializers_expose_expected_fields():
    temperature = TemperatureHistory.objects.create(
        nozzle_actual=200,
        nozzle_target=210,
        bed_actual=60,
        bed_target=65,
    )
    state = PrinterStateHistory.objects.create(
        state="Printing", flags={"printing": True}
    )
    job = PrintJobHistory.objects.create(
        file_name="model.gcode", state="Printing", progress=Decimal("50.00")
    )

    assert set(TemperatureHistorySerializer(temperature).data) == {
        "id",
        "nozzle_actual",
        "nozzle_target",
        "bed_actual",
        "bed_target",
        "recorded_at",
    }
    assert set(PrinterStateHistorySerializer(state).data) == {
        "id",
        "state",
        "flags",
        "recorded_at",
    }
    assert "file_name" in PrintJobHistorySerializer(job).data
    assert "api_key" not in PrintJobHistorySerializer(job).data


@pytest.mark.django_db
def test_latest_endpoints_return_latest_records_and_null_when_empty(api_client):
    empty_status = api_client.get("/api/monitoring/status/")
    empty_temperature = api_client.get("/api/monitoring/temperature/")
    assert empty_status.status_code == 200
    assert empty_status.data == {"data": None}
    assert empty_temperature.data == {"data": None}

    old_state = PrinterStateHistory.objects.create(state="Offline")
    new_state = PrinterStateHistory.objects.create(state="Printing")
    PrinterStateHistory.objects.filter(pk=old_state.pk).update(
        recorded_at=timezone.now() - timedelta(days=1)
    )
    assert api_client.get("/api/monitoring/status/").data["data"]["id"] == new_state.pk

    old_temp = TemperatureHistory.objects.create(
        nozzle_actual=190, nozzle_target=200, bed_actual=50, bed_target=60
    )
    new_temp = TemperatureHistory.objects.create(
        nozzle_actual=205, nozzle_target=210, bed_actual=60, bed_target=65
    )
    TemperatureHistory.objects.filter(pk=old_temp.pk).update(
        recorded_at=timezone.now() - timedelta(days=1)
    )
    assert (
        api_client.get("/api/monitoring/temperature/").data["data"]["id"] == new_temp.pk
    )


@pytest.mark.django_db
def test_history_lists_are_recent_first_paginated_and_filterable(
    api_client, sample_records
):
    temperatures, states, jobs = sample_records
    response = api_client.get("/api/monitoring/temperature/history/?page_size=2")
    assert response.status_code == 200
    assert response.data["count"] == 3
    assert len(response.data["results"]) == 2
    assert response.data["results"][0]["id"] == temperatures[-1].pk

    status_response = api_client.get("/api/monitoring/states/")
    assert status_response.data["results"][0]["id"] == states[-1].pk
    jobs_response = api_client.get("/api/monitoring/jobs/")
    assert jobs_response.data["results"][0]["id"] == jobs[-1].pk

    filtered = api_client.get(
        "/api/monitoring/temperature/history/?start_date=2026-11-21&end_date=2026-11-22"
    )
    assert filtered.status_code == 200
    assert filtered.data["count"] == 2


@pytest.mark.django_db
def test_page_size_is_capped(api_client, sample_records):
    response = api_client.get("/api/monitoring/temperature/history/?page_size=10000")
    assert response.status_code == 200
    assert len(response.data["results"]) <= 100


@pytest.mark.django_db
def test_job_detail_and_not_found(api_client, sample_records):
    job = sample_records[2][0]
    response = api_client.get(f"/api/monitoring/jobs/{job.pk}/")
    assert response.status_code == 200
    assert response.data["id"] == job.pk
    assert api_client.get("/api/monitoring/jobs/99999/").status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "query",
    [
        "start_date=invalid",
        "end_date=2026-02-30",
        "start_date=2026-11-22&end_date=2026-11-21",
    ],
)
def test_invalid_date_filters_return_validation_error(api_client, query):
    response = api_client.get(f"/api/monitoring/states/?{query}")
    assert response.status_code == 400


@pytest.mark.django_db
def test_history_empty_returns_empty_paginated_result(api_client):
    response = api_client.get("/api/monitoring/jobs/")
    assert response.status_code == 200
    assert response.data["count"] == 0
    assert response.data["results"] == []
