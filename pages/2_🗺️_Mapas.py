import streamlit as st
import streamlit.components.v1 as components
from utils import load_data, aplicar_estilo_comum
from config_mapas import LINKS_MAPAS

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Panorama Geográfico")
aplicar_estilo_comum()

df = load_data()

st.markdown('<h1 class="gradient-text">🗺️ Inteligência Geográfica</h1>', unsafe_allow_html=True)
st.caption("Analise indicadores espaciais de forma isolada ou comparativa.")

# Criando as abas internas
tab_geral, tab_comparador = st.tabs(["📋 Visão Geral (Todos os Mapas)", "⚖️ Comparador Lado a Lado"])

# --- ABA 1: VISÃO GERAL ---
with tab_geral:
    st.markdown("### Painel de Exibição Completa")
    c1, c2 = st.columns([1, 2])
    with c1:
        ano_geral = st.selectbox("Selecione o Ano:", sorted(df['Ano'].unique(), reverse=True), key="ano_g")
    with c2:
        locais_disp = list(LINKS_MAPAS.get(ano_geral, {}).keys())
        local_geral = st.selectbox("Selecione a Localidade:", locais_disp, index=locais_disp.index("CE") if "CE" in locais_disp else 0, key="loc_g")

    st.divider()

    mapas_geral = LINKS_MAPAS.get(ano_geral, {}).get(local_geral, {})
    if not mapas_geral:
        st.info("Nenhum mapa configurado para esta seleção.")
    else:
        lista_mapas = []
        if "Violência (Homicídios)" in mapas_geral:
            lista_mapas.append({"t": "🔴 Homicídios", "u": mapas_geral["Violência (Homicídios)"]})
        
        gestao = mapas_geral.get("Gestão Pública (IGMA)", {})
        if isinstance(gestao, dict):
            for p, u in gestao.items():
                lista_mapas.append({"t": f"🟢 IGMA: {p}", "u": u})

        for item in lista_mapas:
            if isinstance(item["u"], str) and item["u"].startswith("http"):
                st.markdown(f"#### {item['t']}")
                # Altura aumentada para evitar cortes
                estilo = 'background: #F8FAFC; padding: 20px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 30px;'
                iframe = f'<iframe src="{item["u"]}" width="100%" height="850" frameborder="0" scrolling="no" style="background: white;"></iframe>'
                components.html(f'<div style="{estilo}">{iframe}</div>', height=950)

# --- ABA 2: COMPARADOR LADO A LADO ---
with tab_comparador:
    st.markdown("### Comparação entre Localidades ou Temas")
    
    anos_c = sorted(df['Ano'].unique(), reverse=True)
    col_l, col_r = st.columns(2)

    def interface_comparacao(lado_id, titulo_default):
        st.subheader(titulo_default)
        a = st.selectbox("Ano:", anos_c, key=f"a_{lado_id}")
        
        locais = list(LINKS_MAPAS.get(a, {}).keys())
        l = st.selectbox("Localidade (Cidade/UF):", locais, key=f"l_{lado_id}")
        
        t = st.selectbox("Tema:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], key=f"t_{lado_id}")
        
        url_c = ""
        try:
            dados = LINKS_MAPAS.get(a, {}).get(l, {})
            if t == "Violência (Homicídios)":
                # ESPAÇADOR PARA ALINHAMENTO:
                # Ocupa o lugar onde estaria o selectbox de pilares para manter os mapas alinhados
                st.markdown('<div style="height: 88px;"></div>', unsafe_allow_html=True)
                url_c = dados.get("Violência (Homicídios)", "")
            else:
                p_disp = list(dados.get("Gestão Pública (IGMA)", {}).keys())
                p = st.selectbox("Pilar da Gestão:", p_disp, key=f"p_{lado_id}")
                url_c = dados.get("Gestão Pública (IGMA)", {}).get(p, "")
        except: 
            url_c = ""

        # Renderização com altura ajustada (850px para o mapa)
        if isinstance(url_c, str) and url_c.startswith("http"):
            estilo_c = 'background: white; padding: 10px; border-radius: 10px; border: 1px solid #E2E8F0;'
            iframe_c = f'<iframe src="{url_c}" width="100%" height="850" frameborder="0" scrolling="no"></iframe>'
            components.html(f'<div style="{estilo_c}">{iframe_c}</div>', height=900)
        else:
            st.warning("Mapa não configurado ou link inválido.")

    with col_l:
        interface_comparacao("esq", "Cenário A")
    with col_r:
        interface_comparacao("dir", "Cenário B")
