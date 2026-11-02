def test_client_initialization(settings):
    from printer.services.octoprint import OctoPrintClient

    settings.OCTOPRINT_URL = "http://localhost:5000"
    settings.OCTOPRINT_API_KEY = "test-api-key"
    settings.OCTOPRINT_TIMEOUT = 10

    client = OctoPrintClient()

    assert client.base_url == "http://localhost:5000"
    assert client.api_key == "test-api-key"
    assert client.timeout == 10
    assert client.headers == {
        "X-Api-Key": "test-api-key"
    }