import streamlit as st
import streamlit.components.v1 as components
from utils import load_data, aplicar_estilo_comum
from config_mapas import LINKS_MAPAS

st.set_page_config(layout="wide", page_title="Panorama Geográfico")
aplicar_estilo_comum()

df = load_data()
st.title("🗺️ Panorama Geográfico")

m1, m2, m3, m4 = st.columns([1, 1, 1.5, 1.5])
with m1: escopo = st.radio("Nível:", ["Brasil", "Estado"])
with m2: 
    lista_ufs = sorted(df['UF'].unique())
    uf = st.selectbox("UF:", lista_ufs, index=lista_ufs.index("CE") if "CE" in lista_ufs else 0) if escopo == "Estado" else "Brasil"
with m3: tema = st.radio("Tema:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], horizontal=True)
with m4:
    pilar = st.selectbox("Pilar:", ["IGMA Geral", "Desenvolvimento Socioeconômico e Ordem Pública", "Educação", "Saúde e Bem-Estar"]) if tema == "Gestão Pública (IGMA)" else None

ano = st.selectbox("Ano de Referência", sorted(df['Ano'].unique(), reverse=True))

# Lógica de URL
try:
    url = LINKS_MAPAS.get(ano, {}).get(uf, {}).get(tema, "") if tema == "Violência (Homicídios)" else LINKS_MAPAS.get(ano, {}).get(uf, {}).get(tema, {}).get(pilar, "")
except: url = ""

if isinstance(url, str) and url.startswith("http"):
    # Quebrando o estilo e as tags em variáveis simples de uma linha (sem aspas triplas!)
    estilo_div = "background-color: #F8FAFC; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0;"
    estilo_iframe = "width: 100%; min-width: 100% !important; border: none;"
    
    # Montando a tag iframe
    tag_iframe = f'<iframe src="{url}" style="{estilo_iframe}" height="750" frameborder="0" scrolling="auto" allowfullscreen="true"></iframe>'
    
    # Juntando tudo na div final
    html_final = f'<div style="{estilo_div}">{tag_iframe}</div>'
    
    components.html(html_final, height=800)
else:
    st.warning("Mapa não disponível para esta seleção.")
