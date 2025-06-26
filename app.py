import streamlit as st
from database import init_db, add_agendamento, get_agendamentos, delete_agendamento
from utils import get_salas, formatar_agendamento
from datetime import datetime, time, timedelta
import pandas as pd
import plotly.graph_objects as go
import time as t

# Configuração da página
st.set_page_config("Agenda Corporativa", layout="wide")

# --- CSS Estilizado ---
st.markdown("""
    <style>
    .main {
        background-color: #F5F7F2;
    }
    .sidebar .sidebar-content {
        background-color: #E6EAE1;
        border-right: 2px solid #A5B299;
    }
    .stButton > button {
        background-color: #687C58;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 8px 16px;
    }
    input, select, textarea {
        border-radius: 8px !important;
        padding: 8px !important;
        border: 1px solid #ccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# Inicializa banco de dados
init_db()

st.title("📅 Agenda Corporativa")

# --- Menu lateral ---
with st.sidebar:
    st.subheader("🔘 Menu Principal")
    menu_choice = st.radio("Ação:", ["Visualizar e Agendar", "Excluir Agendamento"])

# --- VISUALIZAR + AGENDAR ---
if menu_choice == "Visualizar e Agendar":
    col1, col2 = st.columns([3, 1])

    # === VISUALIZAÇÃO DO CALENDÁRIO COM NAVEGAÇÃO DE SEMANAS ===
    with col1:
        st.subheader("📆 Visualização Semanal por Sala")

        # Inicializa semana atual
        if "semana_atual" not in st.session_state:
            hoje = datetime.now()
            st.session_state.semana_atual = hoje - timedelta(days=hoje.weekday())

        # Navegação
        col_nav1, col_nav2, col_nav3 = st.columns([1, 1, 1])
        with col_nav1:
            if st.button("⬅️ Semana anterior"):
                st.session_state.semana_atual -= timedelta(days=7)
        with col_nav2:
            if st.button("🔁 Semana atual"):
                hoje = datetime.now()
                st.session_state.semana_atual = hoje - timedelta(days=hoje.weekday())
        with col_nav3:
            if st.button("➡️ Próxima semana"):
                st.session_state.semana_atual += timedelta(days=7)

        inicio_semana = st.session_state.semana_atual
        fim_semana = inicio_semana + timedelta(days=6)
        st.markdown(f"**Semana: {inicio_semana.date()} até {fim_semana.date()}**")

        agendamentos = get_agendamentos()
        if not agendamentos:
            st.info("Nenhum agendamento encontrado.")
        else:
            df = pd.DataFrame(agendamentos, columns=["ID", "Nome", "Sala", "Data", "Início", "Fim"])
            df["Início"] = pd.to_datetime(df["Data"] + " " + df["Início"])
            df["Fim"] = pd.to_datetime(df["Data"] + " " + df["Fim"])
            df["Data"] = pd.to_datetime(df["Data"]).dt.date
            df = df[(df["Data"] >= inicio_semana.date()) & (df["Data"] <= fim_semana.date())]
            df = df.sort_values(by=["Data", "Início"])

            if df.empty:
                st.warning("📭 Nenhum agendamento nesta semana.")
            else:
                salas = get_salas()
                dias = [inicio_semana.date() + timedelta(days=i) for i in range(7)]
                fig = go.Figure()

                cor_sala = {
                    "Sala 1": "#A3D9FF",
                    "Sala 2": "#C3F584",
                    "Sala 3": "#FFBCBC"
                }

                for _, row in df.iterrows():
                    data = row["Data"]
                    sala = row["Sala"]
                    nome = row["Nome"]
                    start = row["Início"]
                    end = row["Fim"]

                    dia_idx = dias.index(data)
                    sala_idx = salas.index(sala)

                    # Largura fracionada por sala
                    x0 = dia_idx + sala_idx * (0.9 / len(salas))
                    x1 = x0 + (0.9 / len(salas))

                    y0 = start.hour + start.minute / 60
                    y1 = end.hour + end.minute / 60

                    cor = cor_sala.get(sala, "#CCCCCC")

                    fig.add_shape(
                        type="rect",
                        x0=x0, x1=x1, y0=y0, y1=y1,
                        fillcolor=cor,
                        opacity=0.85,
                        line=dict(color="black", width=1)
                    )

                    fig.add_annotation(
                        x=(x0 + x1) / 2,
                        y=(y0 + y1) / 2,
                        text=f"{nome}<br><span style='font-size:10px'>{sala}</span>",
                        showarrow=False,
                        font=dict(size=11),
                        align="center"
                    )

                tickvals = [i + 0.45 for i in range(len(dias))]
                ticktext = [d.strftime("%a %d/%m") for d in dias]

                fig.update_layout(
                    title="📚 Agenda Semanal com Salas Lado a Lado",
                    xaxis=dict(
                        tickmode="array",
                        tickvals=tickvals,
                        ticktext=ticktext,
                        title="Dias da Semana",
                        showgrid=True
                    ),
                    yaxis=dict(
                        range=[7, 20],
                        title="Hora do Dia",
                        dtick=1,
                        showgrid=True
                    ),
                    height=650,
                    margin=dict(l=20, r=20, t=40, b=20),
                    plot_bgcolor="white"
                )

                st.plotly_chart(fig, use_container_width=True)

    # === FORMULÁRIO DE AGENDAMENTO ===
    with col2:
        st.subheader("➕ Novo Agendamento")
        with st.form("agendar_form"):
            nome = st.text_input("Seu nome")
            sala = st.selectbox("Sala", get_salas())
            data = st.date_input("Data")
            hora_inicio = st.time_input("Início", time(9, 0))
            hora_fim = st.time_input("Fim", time(10, 0))
            submit = st.form_submit_button("Agendar")

            if submit:
                if hora_fim <= hora_inicio:
                    st.error("❌ Horário final deve ser após o horário inicial.")
                elif nome.strip() == "":
                    st.error("❌ Nome obrigatório.")
                else:
                    sucesso = add_agendamento(nome, sala, data.strftime("%Y-%m-%d"),
                                              hora_inicio.strftime("%H:%M"),
                                              hora_fim.strftime("%H:%M"))
                    if sucesso:
                        with st.empty():
                            st.success("✅ Agendamento realizado com sucesso!")
                            t.sleep(1.5)
                            st.experimental_rerun()
                    else:
                        st.warning("⚠️ Conflito detectado na agenda.")

# --- EXCLUIR AGENDAMENTO ---
elif menu_choice == "Excluir Agendamento":
    st.subheader("🗑️ Excluir Agendamento Existente")
    agendamentos = get_agendamentos()
    if agendamentos:
        opcoes = [f"{a[0]} - {formatar_agendamento(a)}" for a in agendamentos]
        escolha = st.selectbox("Selecione um agendamento", opcoes)
        if st.button("Excluir"):
            id_excluir = int(escolha.split(" - ")[0])
            delete_agendamento(id_excluir)
            st.success("Agendamento excluído com sucesso.")
            t.sleep(1.5)
            st.experimental_rerun()
    else:
        st.info("Nenhum agendamento para excluir.")
