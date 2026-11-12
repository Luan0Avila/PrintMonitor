from django.contrib import admin

from monitoring.models import (
    PrinterStateHistory,
    PrintJobHistory,
    TemperatureHistory,
)


@admin.register(TemperatureHistory)
class TemperatureHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "nozzle_actual",
        "nozzle_target",
        "bed_actual",
        "bed_target",
        "recorded_at",
    )
    list_filter = ("recorded_at",)
    ordering = ("-recorded_at",)


@admin.register(PrinterStateHistory)
class PrinterStateHistoryAdmin(admin.ModelAdmin):
    list_display = ("state", "recorded_at")
    list_filter = ("state", "recorded_at")
    ordering = ("-recorded_at",)


@admin.register(PrintJobHistory)
class PrintJobHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "file_name",
        "state",
        "progress",
        "print_time",
        "started_at",
        "completed_at",
    )
    list_filter = ("state", "created_at")
    search_fields = ("file_name",)
    ordering = ("-created_at",)