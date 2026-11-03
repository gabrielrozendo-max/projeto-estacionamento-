import streamlit as st
from src.services.streamlit_client import get_status, StreamlitClientError

st.set_page_config(
    page_title="Sistema de Estacionamento",
    page_icon="🚗"
)

st.title("Sistema de Estacionamento")

st.subheader("Situação do estacionamento")

try:
    status_data = get_status()
    if not isinstance(status_data, dict):
        st.error("Ocorreu um erro ao carregar o estado do parque.")
    else:
        max_capacity = status_data.get("max_capacity")
        occupied_spaces = status_data.get("occupied_spaces")
        available_spaces = status_data.get("available_spaces")

        def _is_valid_count(val):
            return isinstance(val, int) and not isinstance(val, bool) and val >= 0

        if not (
            _is_valid_count(max_capacity)
            and _is_valid_count(occupied_spaces)
            and _is_valid_count(available_spaces)
        ):
            st.error("Ocorreu um erro ao carregar o estado do parque.")
        else:
            col1, col2, col3 = st.columns(3)
            col1.metric("Capacidade total", max_capacity)
            col2.metric("Vagas ocupadas", occupied_spaces)
            col3.metric("Vagas disponíveis", available_spaces)
except StreamlitClientError as e:
    st.error(e.message)
except Exception:
    st.error("Ocorreu um erro ao carregar o estado do parque.")
