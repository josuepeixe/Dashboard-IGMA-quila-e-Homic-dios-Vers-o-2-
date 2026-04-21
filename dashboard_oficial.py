import streamlit as st
from utils import load_data, aplicar_estilo_comum

st.set_page_config(layout="wide", page_title="Monitor de Gestão e Segurança", page_icon="🇧🇷")
aplicar_estilo_comum()

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.markdown('<h1 class="gradient-text">Monitor: Gestão Pública vs Segurança</h1>', unsafe_allow_html=True)
st.caption("Visão Geral do Impacto do Desenvolvimento Municipal.")

# Filtros rápidos na Home
anos = sorted(df['Ano'].dropna().unique())
col_ano, _ = st.columns([1, 3])
with col_ano:
    filtro_ano = st.selectbox("📅 Ano de Referência", anos, index=len(anos)-1)

df_filtrado = df[df['Ano'] == filtro_ano]

st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
with k1: st.markdown(f'<div class="card"><div class="kpi-title">Cidades</div><div class="kpi-value">{len(df_filtrado)}</div></div>', unsafe_allow_html=True)
with k2: st.markdown(f'<div class="card"><div class="kpi-title">Média IGMA</div><div class="kpi-value">{df_filtrado["IGMA"].mean():.2f}</div></div>', unsafe_allow_html=True)
with k3: st.markdown(f'<div class="card"><div class="kpi-title">Homicídios (100k)</div><div class="kpi-value">{df_filtrado["Taxa_Homicidios_100k"].mean():.2f}</div></div>', unsafe_allow_html=True)
with k4: st.markdown(f'<div class="card"><div class="kpi-title">População Total</div><div class="kpi-value">{df_filtrado["Populacao"].sum():,.0f}</div></div>', unsafe_allow_html=True)

st.info("👈 Utilize o menu lateral para navegar entre as análises detalhadas.")
