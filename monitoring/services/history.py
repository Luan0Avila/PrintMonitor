from monitoring.models import TemperatureHistory


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