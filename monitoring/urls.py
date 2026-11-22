from django.urls import path

from monitoring.views import (
    LatestPrinterStatusView,
    LatestTemperatureView,
    PrinterStateHistoryListView,
    PrintJobDetailView,
    PrintJobHistoryListView,
    TemperatureHistoryListView,
)

urlpatterns = [
    path("status/", LatestPrinterStatusView.as_view(), name="monitoring-status"),
    path(
        "temperature/", LatestTemperatureView.as_view(), name="monitoring-temperature"
    ),
    path(
        "temperature/history/",
        TemperatureHistoryListView.as_view(),
        name="temperature-history",
    ),
    path(
        "states/", PrinterStateHistoryListView.as_view(), name="printer-state-history"
    ),
    path("jobs/", PrintJobHistoryListView.as_view(), name="print-job-history"),
    path("jobs/<int:id>/", PrintJobDetailView.as_view(), name="print-job-detail"),
]
