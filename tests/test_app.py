import json
from importlib import reload
from unittest.mock import patch

import requests

import config
from app import create_app


def create_client(base_url="https://example.xano.io/api:parking"):
    app = create_app(
        {
            "TESTING": True,
            "XANO_BASE_URL": base_url,
            "XANO_API_KEY": "",
            "XANO_TIMEOUT_SECONDS": 2,
        }
    )
    return app.test_client()


def create_upstream_response(status_code, body):
    response = requests.Response()
    response.status_code = status_code
    response.url = "https://example.xano.io"
    response.headers["Content-Type"] = "application/json"
    response._content = json.dumps(body).encode("utf-8")
    return response


def test_dashboard_renders_operator_forms_and_autofocus():
    response = create_client().get("/")

    assert response.status_code == 200
    assert b'<html lang="pt-PT">' in response.data
    assert b'id="entry-plate"' in response.data
    assert b'autofocus' in response.data
    assert b"Confirmar pagamento" in response.data


def test_status_is_proxied_to_xano():
    upstream = create_upstream_response(
        200,
        {
            "max_capacity": 50,
            "occupied_spaces": 12,
            "available_spaces": 38,
        },
    )

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().get("/api/status")

    assert response.status_code == 200
    assert response.json["available_spaces"] == 38
    request_mock.assert_called_once_with(
        "GET",
        "https://example.xano.io/api:parking/status",
        json=None,
        headers={"Accept": "application/json"},
        timeout=2,
        allow_redirects=False,
    )


def test_xano_api_key_is_read_from_environment_and_forwarded_as_bearer_token(
    monkeypatch,
):
    monkeypatch.setenv("XANO_BASE_URL", "https://example.xano.io/api:parking")
    monkeypatch.setenv("XANO_API_KEY", "test-token")
    config_module = reload(config)
    app = create_app(
        {
            "TESTING": True,
            "XANO_BASE_URL": config_module.Config.XANO_BASE_URL,
            "XANO_API_KEY": config_module.Config.XANO_API_KEY,
            "XANO_TIMEOUT_SECONDS": 2,
        }
    )
    upstream = create_upstream_response(200, {"max_capacity": 10})

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = app.test_client().get("/api/status")

    assert response.status_code == 200
    assert request_mock.call_args.kwargs["headers"] == {
        "Accept": "application/json",
        "Authorization": "Bearer test-token",
    }


def test_xano_url_has_no_hardcoded_default(monkeypatch):
    monkeypatch.delenv("XANO_BASE_URL", raising=False)
    monkeypatch.delenv("XANO_API_KEY", raising=False)
    with patch("dotenv.load_dotenv"):
        config_module = reload(config)

    assert config_module.Config.XANO_BASE_URL == ""
    assert config_module.Config.XANO_API_KEY == ""


def test_entry_validates_and_forwards_snake_case_payload():
    upstream = create_upstream_response(201, {"data": {"id": 7}})

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().post(
            "/api/entries",
            json={"plate": " aa-00-aa ", "vehicle_type": "Carro"},
        )

    assert response.status_code == 201
    assert response.json == {"data": {"id": 7}}
    assert request_mock.call_args.kwargs["json"] == {
        "plate": "AA-00-AA",
        "vehicle_type": "Carro",
    }


def test_exit_preserves_fee_response_and_occupied_spaces():
    exit_body = {
        "data": {
            "id": 7,
            "plate": "AA-00-AA",
            "status": "Aguardando Pagamento",
            "total_cents": 200,
        },
        "occupancy": {"occupied_spaces": 12},
    }
    upstream = create_upstream_response(200, exit_body)

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().post(
            "/api/exits",
            json={"plate": " aa-00-aa "},
        )

    assert response.status_code == 200
    assert response.json == exit_body
    request_mock.assert_called_once_with(
        "POST",
        "https://example.xano.io/api:parking/exits",
        json={"plate": "AA-00-AA"},
        headers={"Accept": "application/json"},
        timeout=2,
        allow_redirects=False,
    )


def test_exit_and_payment_are_proxied_using_contract_payloads():
    client = create_client()
    exit_response = create_upstream_response(
        200,
        {
            "data": {
                "record_id": 7,
                "status": "Aguardando Pagamento",
                "total_cents": 200,
            },
            "occupancy": {"occupied_spaces": 12},
        },
    )
    payment_response = create_upstream_response(
        200,
        {
            "data": {
                "record_id": 7,
                "status": "Concluído",
                "total_cents": 200,
            },
            "occupancy": {
                "occupied_spaces": 11,
                "max_capacity": 50,
            },
        },
    )

    with patch(
        "app.requests.request",
        side_effect=[exit_response, payment_response],
    ) as request_mock:
        exit_result = client.post("/api/exits", json={"plate": "aa-00-aa"})
        payment_result = client.post(
            "/api/payments/confirm",
            json={"record_id": 7},
        )

    assert exit_result.status_code == 200
    assert exit_result.json["data"]["total_cents"] == 200
    assert exit_result.json["occupancy"]["occupied_spaces"] == 12
    assert payment_result.status_code == 200
    assert payment_result.json["data"]["status"] == "Concluído"
    assert payment_result.json["occupancy"]["occupied_spaces"] == 11
    assert payment_result.json["data"]["total_cents"] == 200
    assert request_mock.call_args_list[0].args[:2] == (
        "POST",
        "https://example.xano.io/api:parking/exits",
    )
    assert request_mock.call_args_list[0].kwargs["json"] == {"plate": "AA-00-AA"}
    assert request_mock.call_args_list[1].kwargs["json"] == {"record_id": 7}
    assert request_mock.call_args_list[1].kwargs["headers"] == {
        "Accept": "application/json",
    }
    assert request_mock.call_count == 2


def test_payment_confirmation_preserves_xano_response_and_forwards_record_id():
    payment_body = {
        "data": {
            "record_id": 42,
            "status": "Concluído",
            "total_cents": 375,
        },
        "occupancy": {
            "occupied_spaces": 11,
            "max_capacity": 50,
        },
    }
    upstream = create_upstream_response(200, payment_body)

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().post(
            "/api/payments/confirm",
            json={"record_id": 42},
        )

    assert response.status_code == 200
    assert response.json == payment_body
    request_mock.assert_called_once_with(
        "POST",
        "https://example.xano.io/api:parking/payments/confirm",
        json={"record_id": 42},
        headers={"Accept": "application/json"},
        timeout=2,
        allow_redirects=False,
    )


def test_invalid_payloads_return_structured_json_without_calling_xano():
    client = create_client()
    with patch("app.requests.request") as request_mock:
        missing_vehicle_type = client.post(
            "/api/entries",
            json={"plate": "AA-00-AA"},
        )
        missing_exit_plate = client.post("/api/exits", json={"plate": "  "})
        invalid_payment_results = [
            client.post("/api/payments/confirm", json={"record_id": True}),
            client.post("/api/payments/confirm", json={"record_id": 0}),
            client.post("/api/payments/confirm", json={"record_id": -1}),
            client.post("/api/payments/confirm", json={"record_id": "7"}),
            client.post("/api/payments/confirm", json={}),
            client.post(
                "/api/payments/confirm",
                data="not-json",
                content_type="application/json",
            ),
        ]

    assert missing_vehicle_type.status_code == 400
    assert missing_vehicle_type.json["error"] is True
    assert missing_exit_plate.status_code == 400
    assert missing_exit_plate.json["error"] is True
    assert all(result.status_code == 400 for result in invalid_payment_results)
    assert all(result.json["error"] is True for result in invalid_payment_results)
    request_mock.assert_not_called()


def test_exit_xano_http_error_remains_a_structured_error():
    upstream = create_upstream_response(
        404,
        {"error": {"message": "Não existe registo ativo para esta matrícula."}},
    )

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().post(
            "/api/exits",
            json={"plate": "AA-00-AA"},
        )

    assert response.status_code == 404
    assert response.json == {
        "error": True,
        "message": "Não existe registo ativo para esta matrícula.",
    }
    request_mock.assert_called_once()


def test_exit_network_error_returns_gateway_error():
    with patch(
        "app.requests.request",
        side_effect=requests.exceptions.ConnectionError,
    ) as request_mock:
        response = create_client().post(
            "/api/exits",
            json={"plate": "AA-00-AA"},
        )

    assert response.status_code == 502
    assert response.json["error"] is True
    request_mock.assert_called_once()


def test_payment_confirmation_xano_conflict_is_returned_as_structured_error():
    upstream = create_upstream_response(
        409,
        {
            "error": {
                "code": "PAYMENT_NOT_PENDING",
                "message": "O registo não aguarda pagamento.",
            },
        },
    )

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().post(
            "/api/payments/confirm",
            json={"record_id": 42},
        )

    assert response.status_code == 409
    assert response.json == {
        "error": True,
        "message": "O registo não aguarda pagamento.",
    }
    request_mock.assert_called_once()


def test_payment_confirmation_network_error_returns_gateway_error():
    with patch(
        "app.requests.request",
        side_effect=requests.exceptions.ConnectionError,
    ) as request_mock:
        response = create_client().post(
            "/api/payments/confirm",
            json={"record_id": 42},
        )

    assert response.status_code == 502
    assert response.json == {
        "error": True,
        "message": "Não foi possível estabelecer ligação ao Xano.",
    }
    request_mock.assert_called_once()


def test_xano_http_errors_keep_status_and_use_standard_json():
    upstream = create_upstream_response(
        422,
        {"error": {"message": "O tipo de veículo não tem tarifa."}},
    )

    with patch("app.requests.request", return_value=upstream):
        response = create_client().post(
            "/api/entries",
            json={"plate": "AA-00-AA", "vehicle_type": "Carro"},
        )

    assert response.status_code == 422
    assert response.json == {
        "error": True,
        "message": "O tipo de veículo não tem tarifa.",
    }


def test_network_and_invalid_xano_configuration_return_json_errors():
    with patch(
        "app.requests.request",
        side_effect=requests.exceptions.Timeout,
    ):
        timeout_response = create_client().get("/api/status")

    unconfigured_response = create_client("").get("/api/status")

    assert timeout_response.status_code == 504
    assert timeout_response.json["error"] is True
    assert unconfigured_response.status_code == 503
    assert unconfigured_response.json["error"] is True


def test_unexpected_errors_are_returned_as_structured_json():
    with patch("app.requests.request", side_effect=ValueError("unexpected")):
        response = create_client().get("/api/status")

    assert response.status_code == 500
    assert response.json == {
        "error": True,
        "message": "Ocorreu um erro interno na aplicação.",
    }


def test_get_tarifas_proxied_to_xano():
    upstream = create_upstream_response(
        200,
        {
            "hora_inicial": 10.0,
            "hora_adicional": 5.0,
            "tolerancia_minutos": 15,
        },
    )

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().get("/api/tarifas")

    assert response.status_code == 200
    assert response.json["hora_inicial"] == 10.0
    assert response.json["tolerancia_minutos"] == 15
    request_mock.assert_called_once_with(
        "GET",
        "https://example.xano.io/api:parking/tarifas",
        json=None,
        headers={"Accept": "application/json"},
        timeout=2,
        allow_redirects=False,
    )


def test_update_tarifas_validates_and_proxies_to_xano():
    payload = {
        "hora_inicial": 12.0,
        "hora_adicional": 6.0,
        "tolerancia_minutos": 20,
    }
    upstream = create_upstream_response(200, {"success": True, "data": payload})

    with patch("app.requests.request", return_value=upstream) as request_mock:
        response = create_client().put("/api/tarifas", json=payload)

    assert response.status_code == 200
    assert response.json["success"] is True
    request_mock.assert_called_once_with(
        "PUT",
        "https://example.xano.io/api:parking/tarifas",
        json=payload,
        headers={"Accept": "application/json"},
        timeout=2,
        allow_redirects=False,
    )


def test_update_tarifas_invalid_payload_returns_400():
    client = create_client()
    with patch("app.requests.request") as request_mock:
        invalid_res_1 = client.put("/api/tarifas", json={"hora_inicial": -5})
        invalid_res_2 = client.put("/api/tarifas", json={"tolerancia_minutos": "quinze"})
        invalid_res_3 = client.put("/api/tarifas", json={"hora_adicional": True})

    assert invalid_res_1.status_code == 400
    assert invalid_res_2.status_code == 400
    assert invalid_res_3.status_code == 400
    request_mock.assert_not_called()
