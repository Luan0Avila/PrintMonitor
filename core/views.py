from django.shortcuts import render
from django.urls import reverse


def home(request):
    context = {
        "printer_name": "Creality Ender 3 V3 SE",
        "poll_interval": 15000,
        "api_urls": {
            "status": reverse("monitoring-status"),
            "temperature": reverse("monitoring-temperature"),
            "temperature_history": reverse("temperature-history"),
            "jobs": reverse("print-job-history"),
        },
    }
    return render(request, "core/home.html", context)
