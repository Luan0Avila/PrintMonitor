from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from printer.services.octoprint import OctoPrintClient, OctoPrintError


class PrinterStatusView(APIView):
    def get(self, request):
        client = OctoPrintClient()

        try:
            data = client.get_dashboard_data()
            return Response(data)

        except OctoPrintError as error:
            return Response(
                {
                    "server": {"online": False},
                    "error": str(error),
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
