import streamlit as st
import plotly.express as px
from utils import load_data, aplicar_estilo_comum

st.set_page_config(layout="wide", page_title="Análise de Correlação")
aplicar_estilo_comum()

df = load_data()
st.title("📈 Correlação: IGMA vs Violência")

anos = sorted(df['Ano'].dropna().unique())
ano = st.selectbox("Selecione o Ano", anos, index=len(anos)-1)
df_f = df[df['Ano'] == ano]

fig = px.scatter(
    df_f, x="IGMA", y="Taxa_Homicidios_100k", color="Regiao",
    size="Populacao", hover_name="Cidade_Exibicao",
    color_discrete_sequence=px.colors.qualitative.Bold, size_max=35, opacity=0.9
)
fig.update_traces(marker=dict(line=dict(width=1.5, color='black')))
fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
st.plotly_chart(fig, use_container_width=True)