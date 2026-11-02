import requests

from django.conf import settings


class OctoPrintClient:

    def __init__(self):
        self.base_url = settings.OCTOPRINT_URL
        self.api_key = settings.OCTOPRINT_API_KEY
        self.timeout = settings.OCTOPRINT_TIMEOUT

        self.headers = {
            "X-Api-Key": self.api_key
        }


    def _get(self, endpoint):

        url = f"{self.base_url}/api/{endpoint}"

        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            return response.json()

        except requests.Timeout:
            raise Exception("Tempo limite de conexão com o OctoPrint.")

        except requests.ConnectionError:
            raise Exception("Não foi possível conectar ao OctoPrint.")

        except requests.HTTPError:
            raise Exception(
                f"Erro HTTP ao consultar OctoPrint: {response.status_code}"
            )

        except requests.RequestException as error:
            raise Exception(f"Erro na requisição: {error}")