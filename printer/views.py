from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from printer.services.octoprint import (
    OctoPrintAuthenticationError,
    OctoPrintClient,
    OctoPrintConflictError,
    OctoPrintConnectionError,
    OctoPrintResponseError,
    OctoPrintTimeoutError,
)


class PrinterStatusView(APIView):

    def get(self, request):
        client = OctoPrintClient()

        try:
            data = client.get_dashboard_data()
            return Response(data, status=status.HTTP_200_OK)

        except OctoPrintTimeoutError:
            return Response(
                {
                    "error": {
                        "code": "octoprint_timeout",
                        "message": "O servidor OctoPrint demorou para responder.",
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except OctoPrintConnectionError:
            return Response(
                {
                    "error": {
                        "code": "octoprint_connection_error",
                        "message": "Não foi possível conectar ao servidor OctoPrint.",
                    }
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except OctoPrintAuthenticationError:
            return Response(
                {
                    "error": {
                        "code": "octoprint_authentication_error",
                        "message": "Falha na autenticação com o OctoPrint.",
                    }
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except OctoPrintConflictError:
            return Response(
                {
                    "error": {
                        "code": "octoprint_conflict",
                        "message": "O OctoPrint não conseguiu executar a operação solicitada.",
                    }
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except OctoPrintResponseError:
            return Response(
                {
                    "error": {
                        "code": "octoprint_response_error",
                        "message": "O OctoPrint retornou uma resposta inválida.",
                    }
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )
