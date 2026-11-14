from monitoring.models import PrinterStateHistory, TemperatureHistory


def save_temperature_history(temperature_data):
    tool = temperature_data.get("tool") or {}
    bed = temperature_data.get("bed") or {}

    if not all(
        key in tool for key in ("actual", "target")
    ):
        return None

    if not all(
        key in bed for key in ("actual", "target")
    ):
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