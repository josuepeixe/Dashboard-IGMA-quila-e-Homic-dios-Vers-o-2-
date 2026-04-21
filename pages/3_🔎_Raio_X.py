import streamlit as st
import plotly.graph_objects as go
from utils import load_data, aplicar_estilo_comum

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Raio-X Municipal")
aplicar_estilo_comum()

df = load_data()

st.markdown('<h1 class="gradient-text">🔎 Raio-X Municipal</h1>', unsafe_allow_html=True)
st.caption("Analise o perfil de gestão de um município ou faça um duelo direto entre duas cidades.")

# 2. Criando as Abas
tab_individual, tab_comparador = st.tabs(["👤 Análise Individual", "⚔️ Duelo de Municípios"])

# Variáveis padrão do Radar
pilares = ['Governança, Eficiência Fiscal e Transparência', 'Educação', 'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana', 'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública']
labels = ['Gov', 'Edu', 'Saúde', 'Infra', 'Sust', 'Desenv']

# ==========================================
# ABA 1: ANÁLISE INDIVIDUAL (Com Filtro de Ano Corrigido)
# ==========================================
with tab_individual:
    c1, c2 = st.columns([1, 2])
    with c1:
        ano_ind = st.selectbox("Ano de Referência:", sorted(df['Ano'].unique(), reverse=True), key="ano_ind")
    
    # Filtra o DF pelo ano ANTES de listar as cidades
    df_ano = df[df['Ano'] == ano_ind]
    
    with c2:
        cidade_sel = st.selectbox("Selecione a Cidade:", sorted(df_ano['Cidade_Exibicao'].unique()), index=None, key="cid_ind")

    if cidade_sel:
        dados_cid = df_ano[df_ano['Cidade_Exibicao'] == cidade_sel].iloc[0]
        medias_uf = df_ano[df_ano['UF'] == dados_cid['UF']].mean(numeric_only=True)

        r1, r2 = st.columns([1.6, 1])
        with r1:
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(r=[dados_cid[p] for p in pilares], theta=labels, fill='toself', name=dados_cid['Cidade'], line_color='#10B981'))
            fig.add_trace(go.Scatterpolar(r=[medias_uf[p] for p in pilares], theta=labels, name=f"Média {dados_cid['UF']}", line=dict(dash='dot'), line_color='white'))
            fig.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=30, b=30, l=40, r=40))
            st.plotly_chart(fig, use_container_width=True)

        with r2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.metric("Taxa de Homicídios", f"{dados_cid['Taxa_Homicidios_100k']:.2f}", delta=f"{dados_cid['Taxa_Homicidios_100k'] - medias_uf['Taxa_Homicidios_100k']:.2f} vs Estado", delta_color="inverse")
            st.metric("Nota IGMA", f"{dados_cid['IGMA']:.2f}", delta=f"{dados_cid['IGMA'] - medias_uf['IGMA']:.2f} vs Estado")
            st.divider()
            st.write(f"**População:** {dados_cid['Populacao']:,.0f} hab.")
            st.write(f"**Região:** {dados_cid['Regiao']}")

# ==========================================
# ABA 2: COMPARADOR (DUELO)
# ==========================================
with tab_comparador:
    st.markdown("### Comparação Direta de Desempenho")
    
    c_ano, c_cid1, c_cid2 = st.columns([1, 1.5, 1.5])
    with c_ano:
        ano_comp = st.selectbox("Ano:", sorted(df['Ano'].unique(), reverse=True), key="ano_comp")
        df_comp = df[df['Ano'] == ano_comp]
        lista_cidades = sorted(df_comp['Cidade_Exibicao'].unique())
    with c_cid1:
        cid1 = st.selectbox("Cidade A (Verde):", lista_cidades, index=0, key="cid1")
    with c_cid2:
        # Pega a segunda cidade da lista para não vir a mesma pré-selecionada
        cid2 = st.selectbox("Cidade B (Laranja):", lista_cidades, index=1 if len(lista_cidades)>1 else 0, key="cid2")

    if cid1 and cid2:
        d1 = df_comp[df_comp['Cidade_Exibicao'] == cid1].iloc[0]
        d2 = df_comp[df_comp['Cidade_Exibicao'] == cid2].iloc[0]

        # 1. Gráfico Radar Sobreposto
        fig_comp = go.Figure()
        
        # Plot da Cidade A (Verde Esmeralda)
        fig_comp.add_trace(go.Scatterpolar(r=[d1[p] for p in pilares], theta=labels, fill='toself', name=d1['Cidade'], line_color='#10B981', fillcolor='rgba(16, 185, 129, 0.4)'))
        
        # Plot da Cidade B (Laranja Vibrante para dar alto contraste)
        fig_comp.add_trace(go.Scatterpolar(r=[d2[p] for p in pilares], theta=labels, fill='toself', name=d2['Cidade'], line_color='#F97316', fillcolor='rgba(249, 115, 22, 0.4)'))
        
        fig_comp.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="rgba(0,0,0,0)", margin=dict(t=40, b=40, l=40, r=40), height=550)
        
        st.plotly_chart(fig_comp, use_container_width=True)

        # 2. Métricas Lado a Lado (Comparação exata entre as duas)
        st.markdown("#### Comparativo de Indicadores Finais")
        m1, m2 = st.columns(2)
        
        with m1:
            st.markdown(f"<h4 style='color: #10B981;'>{d1['Cidade']}</h4>", unsafe_allow_html=True)
            st.metric("IGMA Geral", f"{d1['IGMA']:.2f}")
            st.metric("Taxa Homicídios (100k)", f"{d1['Taxa_Homicidios_100k']:.2f}")
            st.metric("População", f"{d1['Populacao']:,.0f}")

        with m2:
            st.markdown(f"<h4 style='color: #F97316;'>{d2['Cidade']}</h4>", unsafe_allow_html=True)
            
            # Calculando a diferença matemática da Cidade B contra a Cidade A
            dif_igma = d2['IGMA'] - d1['IGMA']
            dif_hom = d2['Taxa_Homicidios_100k'] - d1['Taxa_Homicidios_100k']
            
            # Aqui usamos o delta apontando se a Cidade B foi melhor ou pior que a A
            st.metric("IGMA Geral", f"{d2['IGMA']:.2f}", delta=f"{dif_igma:.2f} vs {d1['Cidade']}")
            st.metric("Taxa Homicídios (100k)", f"{d2['Taxa_Homicidios_100k']:.2f}", delta=f"{dif_hom:.2f} vs {d1['Cidade']}", delta_color="inverse")
            st.metric("População", f"{d2['Populacao']:,.0f}")
