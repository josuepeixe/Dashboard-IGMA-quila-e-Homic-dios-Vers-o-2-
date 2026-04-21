import streamlit as st
import plotly.graph_objects as go
from utils import load_data, aplicar_estilo_comum

st.set_page_config(layout="wide", page_title="Raio-X Municipal")
aplicar_estilo_comum()

df = load_data()
st.title("🔎 Raio-X Municipal")

cidade_sel = st.selectbox("Selecione a Cidade:", sorted(df['Cidade_Exibicao'].unique()), index=None)

if cidade_sel:
    dados_cid = df[df['Cidade_Exibicao'] == cidade_sel].iloc[0]
    medias_uf = df[(df['UF'] == dados_cid['UF']) & (df['Ano'] == dados_cid['Ano'])].mean(numeric_only=True)

    r1, r2 = st.columns([1.6, 1])
    with r1:
        pilares = ['Governança, Eficiência Fiscal e Transparência', 'Educação', 'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana', 'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública']
        labels = ['Gov', 'Edu', 'Saúde', 'Infra', 'Sust', 'Desenv']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[dados_cid[p] for p in pilares], theta=labels, fill='toself', name="Cidade", line_color='#10B981'))
        fig.add_trace(go.Scatterpolar(r=[medias_uf[p] for p in pilares], theta=labels, name="Média Estado", line=dict(dash='dot'), line_color='white'))
        fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    with r2:
        st.metric("Taxa de Homicídios", f"{dados_cid['Taxa_Homicidios_100k']:.2f}", delta=f"{dados_cid['Taxa_Homicidios_100k'] - medias_uf['Taxa_Homicidios_100k']:.2f} vs Estado", delta_color="inverse")
        st.metric("Nota IGMA", f"{dados_cid['IGMA']:.2f}", delta=f"{dados_cid['IGMA'] - medias_uf['IGMA']:.2f} vs Estado")
