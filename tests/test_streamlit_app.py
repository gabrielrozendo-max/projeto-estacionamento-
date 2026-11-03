from pathlib import Path
import runpy
import pytest
from unittest.mock import patch, MagicMock
from src.services.streamlit_client import StreamlitClientError


@pytest.fixture(autouse=True)
def guard_network_and_setup():
    with patch("src.services.streamlit_client.requests.request") as mock_req:
        mock_req.side_effect = RuntimeError("Tentativa de chamada de rede real bloqueada nos testes.")
        yield mock_req


@pytest.fixture
def mock_streamlit_ui():
    with patch("streamlit.set_page_config") as p_config, \
         patch("streamlit.title") as p_title, \
         patch("streamlit.subheader") as p_sub, \
         patch("streamlit.error") as p_error, \
         patch("streamlit.columns") as p_cols:

        col1 = MagicMock()
        col2 = MagicMock()
        col3 = MagicMock()
        p_cols.return_value = (col1, col2, col3)

        yield {
            "error": p_error,
            "col1": col1,
            "col2": col2,
            "col3": col3,
        }


def run_streamlit_app():
    app_path = Path(__file__).resolve().parent.parent / "streamlit_app.py"
    runpy.run_path(str(app_path), run_name="__main__")


def test_streamlit_app_renders_success(mock_streamlit_ui):
    with patch("src.services.streamlit_client.get_status", return_value={
        "max_capacity": 50,
        "occupied_spaces": 12,
        "available_spaces": 31,
    }):
        run_streamlit_app()

    mock_streamlit_ui["error"].assert_not_called()
    mock_streamlit_ui["col1"].metric.assert_called_once_with("Capacidade total", 50)
    mock_streamlit_ui["col2"].metric.assert_called_once_with("Vagas ocupadas", 12)
    mock_streamlit_ui["col3"].metric.assert_called_once_with("Vagas disponíveis", 31)


@pytest.mark.parametrize(
    "invalid_data",
    [
        None,
        [],
        "not-a-dict",
        {"max_capacity": 50, "occupied_spaces": 10},
        {"max_capacity": 50, "occupied_spaces": 10, "available_spaces": "40"},
        {"max_capacity": 50, "occupied_spaces": 10, "available_spaces": -5},
        {"max_capacity": 50, "occupied_spaces": 10, "available_spaces": True},
        {"max_capacity": 50.0, "occupied_spaces": 10, "available_spaces": 40},
    ],
)
def test_streamlit_app_handles_invalid_responses(mock_streamlit_ui, invalid_data):
    with patch("src.services.streamlit_client.get_status", return_value=invalid_data):
        run_streamlit_app()

    mock_streamlit_ui["error"].assert_called_once()
    assert "Ocorreu um erro ao carregar o estado do parque." in mock_streamlit_ui["error"].call_args[0][0]
    mock_streamlit_ui["col1"].metric.assert_not_called()
    mock_streamlit_ui["col2"].metric.assert_not_called()
    mock_streamlit_ui["col3"].metric.assert_not_called()


def test_streamlit_app_handles_client_error(mock_streamlit_ui):
    with patch("src.services.streamlit_client.get_status", side_effect=StreamlitClientError("Erro de ligação.", status_code=502)):
        run_streamlit_app()

    mock_streamlit_ui["error"].assert_called_once_with("Erro de ligação.")
    mock_streamlit_ui["col1"].metric.assert_not_called()
    mock_streamlit_ui["col2"].metric.assert_not_called()
    mock_streamlit_ui["col3"].metric.assert_not_called()


def test_streamlit_app_handles_unexpected_exception(mock_streamlit_ui):
    with patch("src.services.streamlit_client.get_status", side_effect=ValueError("Unexpected internal detail")):
        run_streamlit_app()

    mock_streamlit_ui["error"].assert_called_once()
    assert "Ocorreu um erro ao carregar o estado do parque." in mock_streamlit_ui["error"].call_args[0][0]
    assert "Unexpected internal detail" not in mock_streamlit_ui["error"].call_args[0][0]
    mock_streamlit_ui["col1"].metric.assert_not_called()
    mock_streamlit_ui["col2"].metric.assert_not_called()
    mock_streamlit_ui["col3"].metric.assert_not_called()
