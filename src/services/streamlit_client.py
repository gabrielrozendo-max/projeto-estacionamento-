from urllib.parse import urlparse
import requests
from config import Config


class StreamlitClientError(Exception):
    def __init__(self, message, status_code=500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def _get_error_message(status_code):
    messages = {
        400: "O pedido enviado é inválido.",
        401: "A autenticação é necessária para acessar este recurso.",
        403: "Você não tem autorização para realizar esta operação.",
        404: "O recurso solicitado não foi encontrado.",
        409: "O pedido entra em conflito com o estado atual.",
        422: "Os dados fornecidos não puderam ser processados.",
        500: "Ocorreu um erro interno no servidor.",
        502: "O servidor retornou uma resposta inválida.",
        503: "O serviço está temporariamente indisponível.",
        504: "O servidor demorou muito tempo para responder.",
    }
    return messages.get(status_code, "Ocorreu um erro inesperado.")


def _validate_config():
    base_url = Config.XANO_BASE_URL
    if not base_url:
        raise StreamlitClientError(
            "A integração com o Xano não está configurada.",
            status_code=503,
        )
    try:
        parsed = urlparse(base_url)
    except ValueError:
        raise StreamlitClientError(
            "A integração com o Xano não está configurada com um URL HTTPS válido.",
            status_code=503,
        ) from None
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
    ):
        raise StreamlitClientError(
            "A integração com o Xano não está configurada com um URL HTTPS válido.",
            status_code=503,
        )
    return base_url


def _request(method, endpoint, json_data=None):
    base_url = _validate_config()
    headers = {"Accept": "application/json"}
    if Config.XANO_API_KEY:
        headers["Authorization"] = f"Bearer {Config.XANO_API_KEY}"

    try:
        response = requests.request(
            method,
            f"{base_url}{endpoint}",
            json=json_data,
            headers=headers,
            timeout=Config.XANO_TIMEOUT_SECONDS,
            allow_redirects=False,
        )
    except requests.exceptions.Timeout:
        raise StreamlitClientError(
            "O servidor demorou muito tempo para responder.", status_code=504
        )
    except requests.exceptions.ConnectionError:
        raise StreamlitClientError(
            "Não foi possível conectar ao servidor.", status_code=502
        )
    except requests.exceptions.RequestException:
        raise StreamlitClientError(
            "Não foi possível conectar ao servidor.", status_code=502
        )

    if not 200 <= response.status_code < 300:
        raise StreamlitClientError(
            _get_error_message(response.status_code), status_code=response.status_code
        )

    try:
        return response.json()
    except ValueError:
        raise StreamlitClientError(
            "O servidor retornou uma resposta JSON inválida.", status_code=502
        )


def get_status():
    """Busca o status do estacionamento (capacidade e ocupação) no Xano."""
    return _request("GET", "/status")
