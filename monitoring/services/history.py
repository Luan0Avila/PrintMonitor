from django.utils import timezone

from monitoring.models import PrinterStateHistory, PrintJobHistory, TemperatureHistory


def save_temperature_history(temperature_data):
    tool = temperature_data.get("tool") or {}
    bed = temperature_data.get("bed") or {}

    if not all(key in tool for key in ("actual", "target")):
        return None

    if not all(key in bed for key in ("actual", "target")):
        return None

    return TemperatureHistory.objects.create(
        nozzle_actual=tool["actual"],
        nozzle_target=tool["target"],
        bed_actual=bed["actual"],
        bed_target=bed["target"],
    )


def save_printer_state_history(state_data):
    state = state_data.get("state")
    flags = state_data.get("flags") or {}

    if not state:
        return None

    return PrinterStateHistory.objects.create(
        state=state,
        flags=flags,
    )


def save_print_job_history(job_data):
    file_name = job_data.get("file")
    state = job_data.get("state")

    if not file_name or not state:
        return None

    active_states = {"Printing", "Paused"}

    current_job = (
        PrintJobHistory.objects.filter(completed_at__isnull=True)
        .order_by("-created_at")
        .first()
    )

    if current_job:
        current_job.state = state
        current_job.progress = job_data.get("progress") or 0
        current_job.print_time = job_data.get("print_time")
        current_job.print_time_left = job_data.get("print_time_left")

        if state not in active_states:
            current_job.completed_at = timezone.now()

        current_job.save()
        return current_job

    if state not in active_states:
        return None

    return PrintJobHistory.objects.create(
        file_name=file_name,
        state=state,
        progress=job_data.get("progress") or 0,
        print_time=job_data.get("print_time"),
        print_time_left=job_data.get("print_time_left"),
        started_at=timezone.now(),
    )
