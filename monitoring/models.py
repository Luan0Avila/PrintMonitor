from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class TemperatureHistory(models.Model):
    nozzle_actual = models.FloatField()
    nozzle_target = models.FloatField()

    bed_actual = models.FloatField()
    bed_target = models.FloatField()

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-recorded_at",)
        verbose_name = "Histórico de temperatura"
        verbose_name_plural = "Históricos de temperatura"

    def __str__(self):
        return f"Temperatura registrada em {self.recorded_at}"


class PrinterStateHistory(models.Model):
    state = models.CharField(max_length=50)
    flags = models.JSONField(default=dict, blank=True)

    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Histórico de impressão"
        verbose_name_plural = "Históricos de impressão"

    def __str__(self):
        return f"{self.state} - {self.recorded_at}"


class PrintJobHistory(models.Model):
    file_name = models.CharField(max_length=255)

    state = models.CharField(max_length=50)

    progress = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ],
        default=0,
    )

    print_time = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    print_time_left = models.PositiveIntegerField(
        null=True,
        blank=True,
    )

    started_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-recorded_at",)
        verbose_name = "Histórico de estado"
        verbose_name_plural = "Históricos de estado"

    def __str__(self):
        return f"{self.file_name} - {self.state}"
