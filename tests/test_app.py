import json
from unittest.mock import patch

import requests

from app import create_app


def create_client(base_url="https://example.xano.io/api:parking"):
    app = create_app(
        {
            "TESTING": True,
            "XANO_BASE_URL": base_url,
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


def test_exit_and_payment_are_proxied_using_contract_payloads():
    client = create_client()
    exit_response = create_upstream_response(
        200,
        {"data": {"record_id": 7, "total_cents": 200}},
    )
    payment_response = create_upstream_response(
        200,
        {"data": {"record_id": 7, "status": "Concluído"}},
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
    assert payment_result.status_code == 200
    assert request_mock.call_args_list[0].args[:2] == (
        "POST",
        "https://example.xano.io/api:parking/exits",
    )
    assert request_mock.call_args_list[0].kwargs["json"] == {"plate": "AA-00-AA"}
    assert request_mock.call_args_list[1].kwargs["json"] == {"record_id": 7}


def test_invalid_payloads_return_structured_json_without_calling_xano():
    client = create_client()
    with patch("app.requests.request") as request_mock:
        missing_vehicle_type = client.post(
            "/api/entries",
            json={"plate": "AA-00-AA"},
        )
        invalid_payment_id = client.post(
            "/api/payments/confirm",
            json={"record_id": True},
        )

    assert missing_vehicle_type.status_code == 400
    assert missing_vehicle_type.json["error"] is True
    assert invalid_payment_id.status_code == 400
    assert invalid_payment_id.json["error"] is True
    request_mock.assert_not_called()


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
