from datetime import datetime, time

from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from monitoring.models import (
    PrinterStateHistory,
    PrintJobHistory,
    TemperatureHistory,
)
from monitoring.pagination import MonitoringPagination
from monitoring.serializers import (
    PrinterStateHistorySerializer,
    PrintJobHistorySerializer,
    TemperatureHistorySerializer,
)


class LatestRecordView(APIView):
    model = None
    serializer_class = None
    timestamp_field = "recorded_at"

    def get(self, request):
        record = self.model.objects.order_by(f"-{self.timestamp_field}").first()
        data = self.serializer_class(record).data if record else None
        return Response({"data": data})


class LatestPrinterStatusView(LatestRecordView):
    model = PrinterStateHistory
    serializer_class = PrinterStateHistorySerializer


class LatestTemperatureView(LatestRecordView):
    model = TemperatureHistory
    serializer_class = TemperatureHistorySerializer


class DateFilteredListView(generics.ListAPIView):
    pagination_class = MonitoringPagination
    date_field = "recorded_at"

    def _date_bound(self, value, param, end_of_day=False):
        if value is None:
            return None
        try:
            parsed = parse_date(value)
        except ValueError:
            parsed = None
        if parsed is None:
            raise ValidationError(
                {param: "Informe uma data válida no formato YYYY-MM-DD."}
            )
        bound_time = time.max if end_of_day else time.min
        bound = datetime.combine(parsed, bound_time)
        if timezone.is_aware(timezone.now()):
            bound = timezone.make_aware(bound, timezone.get_current_timezone())
        return bound

    def get_queryset(self):
        queryset = self.model.objects.all().order_by(f"-{self.date_field}")
        start = self._date_bound(
            self.request.query_params.get("start_date"), "start_date"
        )
        end = self._date_bound(
            self.request.query_params.get("end_date"), "end_date", end_of_day=True
        )
        if start and end and start > end:
            raise ValidationError(
                {"end_date": "A data final deve ser igual ou posterior à data inicial."}
            )
        if start:
            queryset = queryset.filter(**{f"{self.date_field}__gte": start})
        if end:
            queryset = queryset.filter(**{f"{self.date_field}__lte": end})
        return queryset


class TemperatureHistoryListView(DateFilteredListView):
    model = TemperatureHistory
    serializer_class = TemperatureHistorySerializer


class PrinterStateHistoryListView(DateFilteredListView):
    model = PrinterStateHistory
    serializer_class = PrinterStateHistorySerializer


class PrintJobHistoryListView(DateFilteredListView):
    model = PrintJobHistory
    serializer_class = PrintJobHistorySerializer
    date_field = "created_at"


class PrintJobDetailView(generics.RetrieveAPIView):
    queryset = PrintJobHistory.objects.all()
    serializer_class = PrintJobHistorySerializer
    lookup_url_kwarg = "id"
