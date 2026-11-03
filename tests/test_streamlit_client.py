import json
import pytest
from unittest.mock import patch
import requests

from src.services.streamlit_client import get_status, StreamlitClientError
import config


@pytest.fixture(autouse=True)
def prevent_real_network_calls(monkeypatch):
    monkeypatch.setattr(config.Config, "XANO_BASE_URL", "https://example.xano.io/api:parking")
    monkeypatch.setattr(config.Config, "XANO_API_KEY", "dummy-secret-token")
    monkeypatch.setattr(config.Config, "XANO_TIMEOUT_SECONDS", 3.0)
    with patch("src.services.streamlit_client.requests.request") as mock_req:
        mock_req.side_effect = RuntimeError("Tentativa de chamada de rede real bloqueada nos testes.")
        yield mock_req


def create_upstream_response(status_code, body=None, content_type="application/json"):
    response = requests.Response()
    response.status_code = status_code
    response.url = "https://example.xano.io"
    response.headers["Content-Type"] = content_type
    if body is not None:
        response._content = json.dumps(body).encode("utf-8")
    else:
        response._content = b""
    return response


def test_get_status_success(monkeypatch):
    monkeypatch.setattr(config.Config, "XANO_API_KEY", "dummy-secret-token")
    monkeypatch.setattr(config.Config, "XANO_TIMEOUT_SECONDS", 3.0)

    upstream = create_upstream_response(
        200,
        {
            "max_capacity": 50,
            "occupied_spaces": 10,
            "available_spaces": 40,
        },
    )

    with patch("src.services.streamlit_client.requests.request", return_value=upstream) as request_mock:
        result = get_status()

    assert result["max_capacity"] == 50
    assert result["occupied_spaces"] == 10
    assert result["available_spaces"] == 40
    request_mock.assert_called_once_with(
        "GET",
        "https://example.xano.io/api:parking/status",
        json=None,
        headers={"Accept": "application/json", "Authorization": "Bearer dummy-secret-token"},
        timeout=3.0,
        allow_redirects=False,
    )


def test_mandatory_https_and_allow_redirects(monkeypatch):
    monkeypatch.setattr(config.Config, "XANO_BASE_URL", "http://example.xano.io/api:parking")

    with pytest.raises(StreamlitClientError) as exc_info:
        get_status()

    assert "URL HTTPS" in exc_info.value.message
    assert exc_info.value.status_code == 503


def test_timeout_error():
    with patch("src.services.streamlit_client.requests.request", side_effect=requests.exceptions.Timeout):
        with pytest.raises(StreamlitClientError) as exc_info:
            get_status()

    assert exc_info.value.status_code == 504
    assert "demorou muito tempo" in exc_info.value.message


def test_connection_error():
    with patch("src.services.streamlit_client.requests.request", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(StreamlitClientError) as exc_info:
            get_status()

    assert exc_info.value.status_code == 502
    assert "conectar" in exc_info.value.message


@pytest.mark.parametrize(
    "status_code, expected_msg",
    [
        (400, "inválido"),
        (401, "autenticação"),
        (403, "autorização"),
        (404, "encontrado"),
        (500, "interno"),
        (503, "indisponível"),
    ],
)
def test_http_error_statuses(monkeypatch, status_code, expected_msg):
    monkeypatch.setattr(config.Config, "XANO_API_KEY", "dummy-secret-token")

    upstream = create_upstream_response(
        status_code,
        {"error": {"message": "SENSITIVE_INTERNAL_TOKEN_SECRET_DETAILS"}}
    )

    with patch("src.services.streamlit_client.requests.request", return_value=upstream):
        with pytest.raises(StreamlitClientError) as exc_info:
            get_status()

    assert exc_info.value.status_code == status_code
    assert expected_msg in exc_info.value.message.lower()
    assert "SENSITIVE_INTERNAL_TOKEN_SECRET_DETAILS" not in exc_info.value.message
    assert "dummy-secret-token" not in exc_info.value.message


def test_invalid_json_response():
    upstream = create_upstream_response(200, body=None, content_type="text/plain")
    upstream._content = b"not-json"

    with patch("src.services.streamlit_client.requests.request", return_value=upstream):
        with pytest.raises(StreamlitClientError) as exc_info:
            get_status()

    assert exc_info.value.status_code == 502
    assert "JSON" in exc_info.value.message


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "   ",
        None,
        "http://insecure.com",
        "ftp://example.com",
        "://malformed",
        "https://[broken",
        "https://user:pass@example.com",
        "https://example.com?query=1",
        "https://example.com#fragment",
    ],
)
def test_invalid_or_missing_base_url(monkeypatch, bad_url):
    monkeypatch.setattr(config.Config, "XANO_BASE_URL", bad_url)

    with pytest.raises(StreamlitClientError) as exc_info:
        get_status()

    assert exc_info.value.status_code == 503
    assert "configurada" in exc_info.value.message or "URL HTTPS" in exc_info.value.message
