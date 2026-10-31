from urllib.parse import urlparse

import requests
from flask import Flask, current_app, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from config import Config


def create_app(config_object=Config):
    app = Flask(__name__)
    if isinstance(config_object, dict):
        app.config.from_mapping(config_object)
    else:
        app.config.from_object(config_object)

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return {
            "error": True,
            "message": _http_error_message(error.code),
        }, error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Erro inesperado na aplicação Flask")
        return _json_error(500, "Ocorreu um erro interno na aplicação.")

    @app.get("/")
    def dashboard():
        return render_template("index.html")

    @app.get("/api/status")
    def get_status():
        return _proxy_request("GET", "/status")

    @app.post("/api/entries")
    def create_entry():
        payload = _read_json_object()
        if isinstance(payload, tuple):
            return payload

        plate = _read_required_text(payload, "plate", "A matrícula é obrigatória.")
        vehicle_type = _read_required_text(
            payload,
            "vehicle_type",
            "O tipo de veículo é obrigatório.",
        )
        if isinstance(plate, tuple):
            return plate
        if isinstance(vehicle_type, tuple):
            return vehicle_type

        return _proxy_request(
            "POST",
            "/entries",
            {"plate": plate.upper(), "vehicle_type": vehicle_type},
        )

    @app.post("/api/exits")
    def create_exit():
        payload = _read_json_object()
        if isinstance(payload, tuple):
            return payload

        plate = _read_required_text(payload, "plate", "A matrícula é obrigatória.")
        if isinstance(plate, tuple):
            return plate

        return _proxy_request("POST", "/exits", {"plate": plate.upper()})

    @app.post("/api/payments/confirm")
    def confirm_payment():
        payload = _read_json_object()
        if isinstance(payload, tuple):
            return payload

        record_id = payload.get("record_id")
        if isinstance(record_id, bool) or not isinstance(record_id, int) or record_id < 1:
            return _json_error(400, "O identificador do registo é inválido.")

        return _proxy_request(
            "POST",
            "/payments/confirm",
            {"record_id": record_id},
        )

    return app


def _read_json_object():
    if not request.is_json:
        return _json_error(400, "O pedido tem de incluir um corpo JSON.")

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return _json_error(400, "O corpo do pedido tem de ser um objeto JSON válido.")

    return payload


def _read_required_text(payload, field_name, message):
    value = payload.get(field_name)
    if not isinstance(value, str) or not value.strip():
        return _json_error(400, message)

    return value.strip()


def _proxy_request(method, endpoint, payload=None):
    base_url = current_app.config.get("XANO_BASE_URL", "").strip().rstrip("/")
    parsed_url = urlparse(base_url)
    if (
        parsed_url.scheme != "https"
        or not parsed_url.netloc
        or parsed_url.username
        or parsed_url.password
        or parsed_url.query
        or parsed_url.fragment
    ):
        return _json_error(
            503,
            "A integração com o Xano não está configurada com um URL HTTPS válido.",
        )

    try:
        upstream_response = requests.request(
            method,
            f"{base_url}{endpoint}",
            json=payload,
            headers={"Accept": "application/json"},
            timeout=current_app.config.get("XANO_TIMEOUT_SECONDS", 5),
            allow_redirects=False,
        )
        upstream_response.raise_for_status()
    except requests.exceptions.Timeout:
        return _json_error(504, "O Xano demorou demasiado tempo a responder.")
    except requests.exceptions.HTTPError as error:
        return _upstream_error(error.response)
    except requests.exceptions.RequestException:
        return _json_error(502, "Não foi possível estabelecer ligação ao Xano.")

    if not 200 <= upstream_response.status_code < 300:
        return _upstream_error(upstream_response)

    try:
        response_body = upstream_response.json()
    except ValueError:
        return _json_error(502, "O Xano devolveu uma resposta JSON inválida.")

    if not isinstance(response_body, dict):
        return _json_error(502, "O Xano devolveu uma resposta JSON inválida.")

    return jsonify(response_body), upstream_response.status_code


def _upstream_error(response):
    if response is None:
        return _json_error(502, "O Xano devolveu uma resposta de erro inválida.")

    message = None
    try:
        body = response.json()
    except ValueError:
        body = None

    if isinstance(body, dict):
        error_body = body.get("error")
        if isinstance(error_body, dict):
            message = error_body.get("message")
        elif isinstance(error_body, str):
            message = error_body
        if not message:
            message = body.get("message")

    if not isinstance(message, str) or not message.strip():
        message = _http_error_message(response.status_code)

    status_code = response.status_code
    if status_code < 400 or status_code > 599:
        status_code = 502

    return _json_error(status_code, message.strip())


def _json_error(status_code, message):
    return jsonify({"error": True, "message": message}), status_code


def _http_error_message(status_code):
    messages = {
        400: "O pedido é inválido.",
        401: "A autenticação é necessária.",
        403: "Não tem autorização para aceder a este recurso.",
        404: "O recurso solicitado não foi encontrado.",
        405: "O método usado não é permitido para este recurso.",
        409: "O pedido entra em conflito com o estado atual do parque.",
        422: "Os dados enviados não puderam ser processados.",
        500: "Ocorreu um erro interno no serviço.",
        502: "O serviço Xano devolveu uma resposta inválida.",
        503: "O serviço Xano está temporariamente indisponível.",
        504: "O serviço Xano demorou demasiado tempo a responder.",
    }
    return messages.get(status_code, "Ocorreu um erro na aplicação.")


app = create_app()


if __name__ == "__main__":
    app.run()
