import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils import load_data, aplicar_estilo_comum

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Monitor de Gestão e Segurança", page_icon="🇧🇷")
aplicar_estilo_comum()

try:
    df = load_data()
except Exception as e:
    st.error(f"Erro ao carregar dados: {e}")
    st.stop()

st.markdown('<h1 class="gradient-text">Monitor: Gestão Pública vs Segurança</h1>', unsafe_allow_html=True)
st.caption("Visão Executiva e Panorama Macro dos Indicadores Brasileiros.")

# 2. Filtro Global e Lógica de Ano Anterior
anos = sorted(df['Ano'].dropna().unique())
col_ano, _ = st.columns([1, 4])
with col_ano:
    ano_atual = st.selectbox("📅 Ano de Referência", anos, index=len(anos)-1)

df_atual = df[df['Ano'] == ano_atual].copy()

# Tenta achar os dados do ano passado para fazer a comparação nos cartões
ano_anterior = ano_atual - 1
df_ant = df[df['Ano'] == ano_anterior] if ano_anterior in anos else pd.DataFrame()

# 3. Cálculo dos KPIs com Delta
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

med_igma = df_atual["IGMA"].mean()
med_hom = df_atual["Taxa_Homicidios_100k"].mean()

if not df_ant.empty:
    dif_igma = med_igma - df_ant["IGMA"].mean()
    dif_hom = med_hom - df_ant["Taxa_Homicidios_100k"].mean()
else:
    dif_igma = dif_hom = 0

with k1: st.metric("Total de Municípios", f"{len(df_atual)}")
with k2: st.metric("Média Nacional IGMA", f"{med_igma:.2f}", delta=f"{dif_igma:.2f}" if not df_ant.empty else None)
with k3: st.metric("Média Homicídios (100k)", f"{med_hom:.2f}", delta=f"{dif_hom:.2f}" if not df_ant.empty else None, delta_color="inverse")
with k4: st.metric("População Coberta", f"{df_atual['Populacao'].sum():,.0f}".replace(",", "."))

st.divider()

# 4. NOVA SEÇÃO: RELACIONAMENTO (CORRELAÇÃO)
st.markdown("### 🔍 Relacionamento: Gestão vs Segurança")
st.caption("Veja como a nota de gestão (IGMA) se comporta em relação à taxa de violência em nível nacional.")

# Cálculo da correlação de Pearson para exibir como texto informativo
correlacao = df_atual[['IGMA', 'Taxa_Homicidios_100k']].corr().iloc[0,1]

fig_corr_home = px.scatter(
    df_atual, x="IGMA", y="Taxa_Homicidios_100k",
    color="Regiao", size="Populacao", hover_name="Cidade",
    trendline="ols", # Adiciona a linha de tendência (requer statsmodels)
    trendline_color_override="white",
    color_discrete_sequence=px.colors.qualitative.Safe,
    opacity=0.5,
    title=f"Dispersão Nacional (Correlação de Pearson: {correlacao:.2f})"
)

fig_corr_home.update_layout(
    height=500, 
    xaxis_title="Nota IGMA", 
    yaxis_title="Taxa de Homicídios (100k)",
    margin=dict(t=50, b=20)
)
st.plotly_chart(fig_corr_home, use_container_width=True, theme="streamlit")

st.divider()

# 5. Gráficos de Distribuição
st.markdown("### 📊 Distribuição dos Indicadores")
c_dist1, c_dist2 = st.columns(2)

with c_dist1:
    fig_hist_igma = px.histogram(df_atual, x="IGMA", nbins=30, color_discrete_sequence=['#10B981'], title="Distribuição das Notas IGMA", opacity=0.8)
    st.plotly_chart(fig_hist_igma, use_container_width=True, theme="streamlit")

with c_dist2:
    fig_hist_hom = px.histogram(df_atual, x="Taxa_Homicidios_100k", nbins=30, color_discrete_sequence=['#EF4444'], title="Distribuição de Homicídios", opacity=0.8)
    st.plotly_chart(fig_hist_hom, use_container_width=True, theme="streamlit")

# 6. Evolução Histórica Macro
st.markdown("### 📈 Evolução Histórica Nacional")
df_evolucao = df.groupby('Ano').agg(IGMA_Medio=('IGMA', 'mean'), Homicidios_Medio=('Taxa_Homicidios_100k', 'mean')).reset_index()

c_line1, c_line2 = st.columns(2)
with c_line1:
    fig_l1 = px.line(df_evolucao, x="Ano", y="IGMA_Medio", markers=True, color_discrete_sequence=['#10B981'], title="Média IGMA Brasil")
    st.plotly_chart(fig_l1, use_container_width=True, theme="streamlit")
with c_line2:
    fig_l2 = px.line(df_evolucao, x="Ano", y="Homicidios_Medio", markers=True, color_discrete_sequence=['#EF4444'], title="Média Homicídios Brasil")
    st.plotly_chart(fig_l2, use_container_width=True, theme="streamlit")

st.info("👈 Utilize o menu lateral para análises detalhadas por cidade e mapas comparativos.")
