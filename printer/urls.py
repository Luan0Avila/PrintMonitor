from django.urls import path
from printer.views import PrinterStatusView

urlpatterns = [
    path("status/", PrinterStatusView.as_view(), name="printer-status"),
]