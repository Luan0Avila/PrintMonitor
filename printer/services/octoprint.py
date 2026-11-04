import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

class OctoPrintError(Exception):
    """Erro base da integração com o OctoPrint."""


class OctoPrintConnectionError(OctoPrintError):
    """Falha de conexão com o servidor OctoPrint."""


class OctoPrintTimeoutError(OctoPrintError):
    """Tempo limite excedido na comunicação."""


class OctoPrintAuthenticationError(OctoPrintError):
    """Falha de autenticação na API."""


class OctoPrintConflictError(OctoPrintError):
    """Operação incompatível com o estado atual."""


class OctoPrintResponseError(OctoPrintError):
    """Erro ou resposta inválida da API."""


class OctoPrintClient:
    def __init__(self):
        self.base_url = settings.OCTOPRINT_URL
        self.api_key = settings.OCTOPRINT_API_KEY
        self.timeout = settings.OCTOPRINT_TIMEOUT
        self.headers = {"X-Api-Key": self.api_key}

    def _get(self, endpoint):
        url = f"{self.base_url}/api/{endpoint}"

        try:
            logger.info("Consultando endpoint do OctoPrint: %s", endpoint)

            response = requests.get(url, headers=self.headers, timeout=self.timeout)

            logger.info("Consulta ao endpoint %s realizada com sucesso.", endpoint)
            response.raise_for_status()
            return response.json()

        except requests.Timeout as error:
            logger.warning(
                "Timeout ao consultar o endpoint %s.",
                endpoint,
            )
            raise OctoPrintTimeoutError(
                "Tempo limite de conexão com o OctoPrint."
            ) from error

        except requests.ConnectionError as error:
            logger.error(
                "Falha de conexão com o OctoPrint."
            )
            raise OctoPrintConnectionError(
                "Não foi possível conectar ao OctoPrint."
            ) from error

        except requests.HTTPError as error:
            status_code = error.response.status_code

            logger.error(
                "Erro HTTP %s ao consultar %s.",
                status_code,
                endpoint,
            )

            if status_code in (401, 403):
                raise OctoPrintAuthenticationError(
                    "Falha de autenticação na API do OctoPrint."
                ) from error

            if status_code == 409:
                raise OctoPrintConflictError(
                    "Operação incompatível com o estado atual do OctoPrint."
                ) from error

            raise OctoPrintResponseError(
                f"Erro HTTP ao consultar o OctoPrint: {status_code}."
            ) from error

        except requests.exceptions.JSONDecodeError as error:
            logger.error(
                "Resposta JSON inválida no endpoint %s.",
                endpoint,
            )
            raise OctoPrintResponseError(
                "O OctoPrint retornou uma resposta JSON inválida."
            ) from error

        except requests.RequestException as error:
            logger.exception(
                "Erro inesperado na requisição ao endpoint %s.",
                endpoint,
            )
            raise OctoPrintResponseError(
                f"Erro na requisição: {error}"
            ) from error
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

        connected = connection_state.get("state") in {
    "Operational",
    "Printing",
    "Paused",
}
        if connected:
            logger.info(
                "Impressora conectada. Estado: %s",
                connection_state.get("state"),
            )
        else:
            logger.warning(
                "Impressora desconectada. Estado: %s",
                connection_state.get("state"),
            )

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
