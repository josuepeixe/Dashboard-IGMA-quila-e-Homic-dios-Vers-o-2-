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
    color_discrete_sequence=px.colors.qualitative.Pastel, # Cores mais suaves
    size_max=35, opacity=0.8
)

# Uma borda cinza média funciona bem tanto no claro quanto no escuro
fig.update_traces(marker=dict(line=dict(width=1, color='Gray')))

# Removemos o template forçado e passamos o controle para o Streamlit
fig.update_layout(
    xaxis_title="Nota IGMA Geral", 
    yaxis_title="Taxa de Homicídios (por 100k)",
    margin=dict(t=30, b=10, l=10, r=10)
)

# O segredo está aqui: theme="streamlit"
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
