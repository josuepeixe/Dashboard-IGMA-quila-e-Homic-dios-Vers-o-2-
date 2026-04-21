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

df_atual = df[df['Ano'] == ano_atual]

# Tenta achar os dados do ano passado para fazer a comparação nos cartões
ano_anterior = ano_atual - 1
df_ant = df[df['Ano'] == ano_anterior] if ano_anterior in anos else pd.DataFrame()

# 3. Cálculo dos KPIs com Delta (Comparação com ano anterior)
st.markdown("<br>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)

# Funções auxiliares para os cartões
qtd_cid = len(df_atual)
med_igma = df_atual["IGMA"].mean()
med_hom = df_atual["Taxa_Homicidios_100k"].mean()
pop_total = df_atual["Populacao"].sum()

if not df_ant.empty:
    dif_igma = med_igma - df_ant["IGMA"].mean()
    dif_hom = med_hom - df_ant["Taxa_Homicidios_100k"].mean()
else:
    dif_igma = dif_hom = 0

with k1: 
    st.metric("Total de Municípios Analisados", f"{qtd_cid}")
with k2: 
    st.metric("Média Nacional IGMA", f"{med_igma:.2f}", delta=f"{dif_igma:.2f} vs {ano_anterior}" if not df_ant.empty else None)
with k3: 
    st.metric("Média Homicídios (100k)", f"{med_hom:.2f}", delta=f"{dif_hom:.2f} vs {ano_anterior}" if not df_ant.empty else None, delta_color="inverse")
with k4: 
    st.metric("População Coberta", f"{pop_total:,.0f}".replace(",", "."))

st.divider()

# 4. CORRELAÇÃO
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

# 5. Gráficos de Distribuição (O que você sugeriu!)
st.markdown("### 📊 Distribuição dos Indicadores")
st.caption(f"Como os municípios estão espalhados em relação às notas e taxas no ano de {ano_atual}.")

c_dist1, c_dist2 = st.columns(2)

with c_dist1:
    fig_hist_igma = px.histogram(
        df_atual, x="IGMA", nbins=30,
        color_discrete_sequence=['#10B981'],
        title="Distribuição das Notas do IGMA",
        opacity=0.8
    )
    fig_hist_igma.update_layout(xaxis_title="Nota IGMA", yaxis_title="Qtd. de Cidades", margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig_hist_igma, use_container_width=True, theme="streamlit")

with c_dist2:
    fig_hist_hom = px.histogram(
        df_atual, x="Taxa_Homicidios_100k", nbins=30,
        color_discrete_sequence=['#EF4444'],
        title="Distribuição das Taxas de Homicídios",
        opacity=0.8
    )
    fig_hist_hom.update_layout(xaxis_title="Taxa por 100k hab.", yaxis_title="Qtd. de Cidades", margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig_hist_hom, use_container_width=True, theme="streamlit")

# 6. Evolução Histórica Macro
st.markdown("### 📈 Evolução Histórica Nacional")
st.caption("Acompanhamento das médias brasileiras ao longo dos anos.")

# Agrupa as médias de todos os anos
df_evolucao = df.groupby('Ano').agg(
    IGMA_Medio=('IGMA', 'mean'),
    Homicidios_Medio=('Taxa_Homicidios_100k', 'mean')
).reset_index()

c_linha1, c_linha2 = st.columns(2)

with c_linha1:
    fig_linha_igma = px.line(df_evolucao, x="Ano", y="IGMA_Medio", markers=True, color_discrete_sequence=['#10B981'], title="Média do IGMA (Brasil)")
    fig_linha_igma.update_traces(line=dict(width=3), marker=dict(size=8))
    fig_linha_igma.update_layout(xaxis=dict(tickmode='linear'), yaxis_title="Nota", margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig_linha_igma, use_container_width=True, theme="streamlit")

with c_linha2:
    fig_linha_hom = px.line(df_evolucao, x="Ano", y="Homicidios_Medio", markers=True, color_discrete_sequence=['#EF4444'], title="Média de Homicídios (Brasil)")
    fig_linha_hom.update_traces(line=dict(width=3), marker=dict(size=8))
    fig_linha_hom.update_layout(xaxis=dict(tickmode='linear'), yaxis_title="Taxa (100k)", margin=dict(t=40, b=20), height=350)
    st.plotly_chart(fig_linha_hom, use_container_width=True, theme="streamlit")

st.info("👈 Utilize o menu lateral para aprofundar as análises por localidade, cruzar dados na Matriz e comparar Mapas.")
