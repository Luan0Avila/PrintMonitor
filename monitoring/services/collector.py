from monitoring.services.history import (
    save_print_job_history,
    save_printer_state_history,
    save_temperature_history,
)
from printer.services.octoprint import OctoPrintClient


def collect_printer_data():
    client = OctoPrintClient()
    dashboard_data = client.get_dashboard_data()

    if not dashboard_data["connection"]["connected"]:
        return dashboard_data

    temperature_data = dashboard_data.get("temperature") or {}
    printer_data = dashboard_data.get("printer") or {}
    job_data = dashboard_data.get("job") or {}

    save_temperature_history(temperature_data)

    save_printer_state_history(
        {
            "state": printer_data.get("state"),
            "flags": printer_data.get("flags"),
        }
    )

    if job_data:
        save_print_job_history(job_data)

    return dashboard_data
