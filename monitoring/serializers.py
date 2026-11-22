from rest_framework import serializers

from monitoring.models import (
    PrinterStateHistory,
    PrintJobHistory,
    TemperatureHistory,
)


class TemperatureHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TemperatureHistory
        fields = (
            "id",
            "nozzle_actual",
            "nozzle_target",
            "bed_actual",
            "bed_target",
            "recorded_at",
        )


class PrinterStateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrinterStateHistory
        fields = ("id", "state", "flags", "recorded_at")


class PrintJobHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PrintJobHistory
        fields = (
            "id",
            "file_name",
            "state",
            "progress",
            "print_time",
            "print_time_left",
            "started_at",
            "completed_at",
            "created_at",
            "updated_at",
        )
