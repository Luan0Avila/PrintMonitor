import requests
from django.conf import settings


class OctoPrintError(Exception):
    """Erro na comunicação com a API do OctoPrint."""


class OctoPrintClient:
    def __init__(self):
        self.base_url = settings.OCTOPRINT_URL
        self.api_key = settings.OCTOPRINT_API_KEY
        self.timeout = settings.OCTOPRINT_TIMEOUT
        self.headers = {"X-Api-Key": self.api_key}

    def _get(self, endpoint):
        url = f"{self.base_url}/api/{endpoint}"

        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            response.raise_for_status()
            return response.json()

        except requests.Timeout as error:
            raise OctoPrintError("Tempo limite de conexão com o OctoPrint.") from error

        except requests.ConnectionError as error:
            raise OctoPrintError("Não foi possível conectar ao OctoPrint.") from error

        except requests.HTTPError as error:
            status_code = error.response.status_code
            raise OctoPrintError(
                f"Erro HTTP ao consultar o OctoPrint: {status_code}."
            ) from error

        except requests.RequestException as error:
            raise OctoPrintError(f"Erro na requisição: {error}") from error

    def get_printer_status(self):
        return self._get("printer")

    def get_current_job(self):
        return self._get("job")

    def get_temperature(self):
        printer_data = self.get_printer_status()
        return printer_data.get("temperature", {})

    def get_connection(self):
        return self._get("connection")

    def get_dashboard_data(self):
        connection = self.get_connection()
        connection_state = connection.get("current", {})

        connected = connection_state.get("state") == "Operational"

        connection_data = {
            "connected": connected,
            "state": connection_state.get("state"),
            "port": connection_state.get("port"),
            "baudrate": connection_state.get("baudrate"),
        }

        if not connected:
            return {
                "server": {"online": True},
                "connection": connection_data,
                "printer": {
                    "state": "Disconnected",
                    "flags": {},
                },
                "temperature": {},
                "job": None,
            }

        printer_data = self.get_printer_status()
        job_data = self.get_current_job()

        printer_state = printer_data.get("state", {})

        return {
            "server": {"online": True},
            "connection": connection_data,
            "printer": {
                "state": printer_state.get("text"),
                "flags": printer_state.get("flags", {}),
            },
            "temperature": printer_data.get("temperature", {}),
            "job": job_data,
        }
