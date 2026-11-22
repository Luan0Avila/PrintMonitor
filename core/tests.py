import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page_renders_dashboard_template(client):
    response = client.get(reverse("core:home"))

    assert response.status_code == 200
    assert "core/home.html" in [template.name for template in response.templates]
    assert b"PrintMonitor" in response.content
    assert b"Nenhuma impress\xc3\xa3o ativa" in response.content


@pytest.mark.django_db
def test_home_page_provides_printer_and_api_context_without_monitoring_data(client):
    response = client.get(reverse("core:home"))

    assert response.context["printer_name"] == "Creality Ender 3 V3 SE"
    assert response.context["poll_interval"] == 15000
    assert response.context["api_urls"] == {
        "status": "/api/monitoring/status/",
        "temperature": "/api/monitoring/temperature/",
        "temperature_history": "/api/monitoring/temperature/history/",
        "jobs": "/api/monitoring/jobs/",
    }
