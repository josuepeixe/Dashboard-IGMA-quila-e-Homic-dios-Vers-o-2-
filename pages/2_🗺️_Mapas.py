import streamlit as st
import streamlit.components.v1 as components
from utils import load_data, aplicar_estilo_comum
from config_mapas import LINKS_MAPAS

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Painel Comparativo de Mapas")
aplicar_estilo_comum()

# 2. Carregar Dados
df = load_data()

st.markdown('<h1 class="gradient-text">🗺️ Painel Comparativo Geográfico</h1>', unsafe_allow_html=True)
st.caption("Visualize e compare todos os indicadores geográficos disponíveis para o recorte selecionado.")

# 3. Filtros de Comparação (Topo da Página)
col_ano, col_escopo, col_uf = st.columns([1, 1, 1.5])

with col_ano:
    anos_disponiveis = sorted(df['Ano'].dropna().unique(), reverse=True)
    ano_sel = st.selectbox("📅 Selecione o Ano:", anos_disponiveis)

with col_escopo:
    escopo = st.radio("📍 Nível de Análise:", ["Brasil", "Estado"], horizontal=True)

with col_uf:
    if escopo == "Estado":
        lista_ufs = sorted(df['UF'].unique())
        # Tenta deixar CE como padrão, senão pega o primeiro
        idx_padrao = lista_ufs.index("CE") if "CE" in lista_ufs else 0
        uf_sel = st.selectbox("Escolha a UF para comparar:", lista_ufs, index=idx_padrao)
    else:
        uf_sel = "Brasil"

st.divider()

# 4. Lógica de Exibição dos Mapas
# Pegamos o dicionário de links para o ano e local selecionados
mapas_disponiveis = LINKS_MAPAS.get(ano_sel, {}).get(uf_sel, {})

if not mapas_disponiveis:
    st.info(f"💡 Não encontramos mapas cadastrados para {uf_sel} no ano {ano_sel}.")
else:
    # Criamos uma lista para organizar o que vamos mostrar
    itens_para_exibir = []

    # 1. Adiciona o mapa de Violência se existir
    if "Violência (Homicídios)" in mapas_disponiveis:
        itens_para_exibir.append({
            "titulo": "🔴 Indicador de Violência (Homicídios)",
            "url": mapas_disponiveis["Violência (Homicídios)"]
        })

    # 2. Adiciona os mapas de Gestão (IGMA) se existirem
    gestao_links = mapas_disponiveis.get("Gestão Pública (IGMA)", {})
    if isinstance(gestao_links, dict):
        for pilar, url in gestao_links.items():
            itens_para_exibir.append({
                "titulo": f"🟢 Gestão Pública: {pilar}",
                "url": url
            })

    # 5. Renderização dos Mapas (Um abaixo do outro para melhor comparação)
    if not itens_para_exibir:
        st.warning("Nenhum link válido encontrado para esta seleção.")
    else:
        st.write(f"### Mostrando {len(itens_para_exibir)} mapas para {uf_sel} ({ano_sel})")
        
        for item in itens_para_exibir:
            url = item["url"]
            # Só renderiza se for um link de verdade
            if isinstance(url, str) and url.startswith("http"):
                st.markdown(f"#### {item['titulo']}")
                
                # Estilo para o fundo claro e bordas
                estilo_div = 'background-color: #F8FAFC; padding: 25px; border-radius: 15px; border: 1px solid #E2E8F0; margin-bottom: 50px;'
                estilo_iframe = 'width: 100%; border: none; background-color: white; border-radius: 10px;'
                
                tag_iframe = f'<iframe src="{url}" style="{estilo_iframe}" height="850" frameborder="0" scrolling="no" allowfullscreen="true"></iframe>'
                html_final = f'<div style="{estilo_div}">{tag_iframe}</div>'
                
                components.html(html_final, height=950)
            else:
                # Opcional: mostrar aviso se o link ainda for "SEU_LINK_AQUI"
                if "SEU_LINK" in str(url):
                     st.caption(f"ℹ️ O mapa para '{item['titulo']}' ainda está em fase de configuração.")
