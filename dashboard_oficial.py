# python -m streamlit run "C:\Users\josue\OneDrive\Área de Trabalho\ARTIGO CIENTIFICO\PYTHON\src\dashboard_oficial.py"

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from config_mapas import LINKS_MAPAS

# Adicione a importação do gsheets aqui:
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Monitor de Gestão e Segurança",
    page_icon="🇧🇷"
)

# ==========================================
# 2. CARREGAMENTO DOS DADOS (MODIFICADO PARA API)
# ==========================================
@st.cache_data(ttl=600) # ttl=600 faz o cache dos dados por 10 min. Assim não sobrecarrega a API do Google.
def load_data():
    # Cria a conexão usando as credenciais que configuramos nos secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    
    # Faz a leitura dos dados puxando do Google Sheets (Retorna um DataFrame do Pandas)
    df = conn.read()
    
    pilares = [
        'Governança, Eficiência Fiscal e Transparência', 
        'Educação', 
        'Saúde e Bem-Estar', 
        'Infraestrutura e Mobilidade Urbana', 
        'Sustentabilidade', 
        'Desenvolvimento Socioeconômico e Ordem Pública'
    ]
    
    # O restante do código original continua o mesmo!
    cols_numericas = ['IGMA', 'Taxa_Homicidios_100k', 'Populacao'] + pilares
    for col in cols_numericas:
        if col in df.columns:
            # O Excel as vezes salva números como string, isso garante o tipo correto
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("ERRO: Arquivo CSV não encontrado. Verifique se ele está na mesma pasta que este script!")
    st.stop()

# ==========================================
# 3. SIDEBAR (FILTROS)
# ==========================================
st.sidebar.header("🔍 Filtros Globais")

anos_disponiveis = sorted(df['Ano'].dropna().unique())
filtro_ano = st.sidebar.selectbox("Selecione o Ano:", anos_disponiveis, index=len(anos_disponiveis)-1)

estados_disponiveveis = sorted(df['UF'].dropna().unique())
filtro_uf = st.sidebar.multiselect("Filtrar por Estado(s):", estados_disponiveveis)

pop_min, pop_max = int(df['Populacao'].min()), int(df['Populacao'].max())
range_pop = st.sidebar.slider("Faixa Populacional:", pop_min, pop_max, (pop_min, pop_max))

df_filtrado = df[df['Ano'] == filtro_ano].copy()
if filtro_uf:
    df_filtrado = df_filtrado[df_filtrado['UF'].isin(filtro_uf)]
df_filtrado = df_filtrado[(df_filtrado['Populacao'] >= range_pop[0]) & (df_filtrado['Populacao'] <= range_pop[1])]

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    <div style="text-align: center;">
        <p style="color: #888; font-size: 13px; margin-bottom: 2px;">Análise e Desenvolvimento:</p>
        <p style="font-weight: bold; font-size: 16px; margin-bottom: 5px;">Josué Peixe</p>
    </div>
    """, unsafe_allow_html=True
)

# ==========================================
# BLOCO 1: MENU DE KPIs BÁSICOS
# ==========================================
st.title("🇧🇷 Monitor: Gestão Pública vs. Segurança")
st.markdown("Plataforma de inteligência de dados para análise do impacto do desenvolvimento municipal na violência letal.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cidades Analisadas", f"{len(df_filtrado):,}".replace(",", "."))
col2.metric("Média IGMA", f"{df_filtrado['IGMA'].mean():.2f}")
col3.metric("Média Homicídios (100k)", f"{df_filtrado['Taxa_Homicidios_100k'].mean():.2f}")
col4.metric("População Coberta", f"{df_filtrado['Populacao'].sum():,.0f}".replace(",", "."))

st.markdown("---")

# ==========================================
# BLOCO 2: GRÁFICO DE DISPERSÃO (HIGHLIGHT)
# ==========================================
st.header(f"📈 Correlação: Violência Letal vs. IGMA ({filtro_ano})")

col_titulo_grafico, col_filtro_regiao = st.columns([3, 1])
with col_filtro_regiao:
    opcoes_regiao = ["Todas as Regiões"] + sorted(df_filtrado['Regiao'].dropna().unique())
    foco_regiao = st.selectbox("Destacar Região:", options=opcoes_regiao)

fig_scatter = go.Figure()

if foco_regiao == "Todas as Regiões":
    fig_scatter = px.scatter(
        df_filtrado, x="IGMA", y="Taxa_Homicidios_100k", color="Regiao",
        size="Populacao", hover_name="Cidade", opacity=0.7,
        size_max=40, template="plotly_white", trendline="ols"
    )
else:
    df_foco = df_filtrado[df_filtrado['Regiao'] == foco_regiao]
    df_fundo = df_filtrado[df_filtrado['Regiao'] != foco_regiao]
    
    fig_scatter.add_trace(go.Scatter(
        x=df_fundo['IGMA'], y=df_fundo['Taxa_Homicidios_100k'], mode='markers',
        marker=dict(color='#E5E7EB', size=df_fundo['Populacao']/30000, sizemode='area', sizemin=3),
        opacity=0.3, name='Outras', hoverinfo='skip'
    ))
    
    fig_scatter.add_trace(go.Scatter(
        x=df_foco['IGMA'], y=df_foco['Taxa_Homicidios_100k'], mode='markers',
        marker=dict(color='#DC2626', size=df_foco['Populacao']/30000, sizemode='area', sizemin=5, line=dict(width=1, color='white')),
        name=foco_regiao, text=df_foco['Cidade'],
        hovertemplate="<b>%{text}</b><br>IGMA: %{x:.2f}<br>Homicídios: %{y:.2f}<extra></extra>"
    ))

fig_scatter.update_layout(
    xaxis_title="Nota IGMA Geral", yaxis_title="Taxa de Homicídios (por 100k)",
    height=500, margin=dict(t=30, b=0), legend_title_text="Região"
)
st.plotly_chart(fig_scatter, width="stretch")

st.markdown("---")

# ==========================================
# BLOCO 3: PANORAMA GEOGRÁFICO (MAPAS)
# ==========================================
st.header("🗺️ Panorama Geográfico")

# Dividindo a tela para acomodar a nova opção de escolha do Estado
col_escopo, col_uf_mapa, col_tema, col_pilar = st.columns([1, 1, 1.2, 1.5])

with col_escopo:
    escopo = st.radio("1. Nível:", ["Brasil", "Por Estado"], key="radio_escopo")

with col_uf_mapa:
    if escopo == "Por Estado":
        # Se escolheu Estado, mostra a lista de UFs (já deixo o CE pré-selecionado se existir)
        lista_ufs = sorted(df['UF'].unique())
        index_padrao = lista_ufs.index("CE") if "CE" in lista_ufs else 0
        uf_escolhida = st.selectbox("2. Escolha a UF:", lista_ufs, index=index_padrao)
    else:
        uf_escolhida = "Brasil"
        st.write("") # Apenas um espaço em branco para manter o layout alinhado

with col_tema:
    tema = st.radio("3. Tema:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], key="radio_tema")

with col_pilar:
    if tema == "Gestão Pública (IGMA)":
        pilar_escolhido = st.selectbox("4. Escolha o Pilar:", ["IGMA Geral", "Desenvolvimento Socioeconômico e Ordem Pública"])
    else:
        st.info(f"Visualizando Homicídios de {filtro_ano}.")


# Lógica à prova de falhas para buscar o link correto do Dicionário
url_mapa = ""
try:
    # 1. Pega os mapas do Ano selecionado (ex: 2022)
    dict_do_ano = LINKS_MAPAS.get(filtro_ano, {})
    # 2. Pega os mapas do local selecionado (ex: "Brasil" ou "CE")
    dict_do_local = dict_do_ano.get(uf_escolhida, {})
    
    if tema == "Violência (Homicídios)":
        url_mapa = dict_do_local.get(tema, "")
    else:
        url_mapa = dict_do_local.get(tema, {}).get(pilar_escolhido, "")
except Exception:
    url_mapa = ""

if url_mapa and "SEU_LINK" not in url_mapa:
    # ALTURA DO MAPA AUMENTADA PARA 850
    components.iframe(url_mapa, height=850, scrolling=False)
else:
    st.warning(f"🔗 O mapa para **{uf_escolhida} em {filtro_ano}** ainda não possui um link. Adicione no dicionário 'LINKS_MAPAS' no código.")

st.markdown("---")

# ==========================================
# BLOCO 4: RAIO-X MUNICIPAL (RADAR)
# ==========================================
st.header(f"🔎 Raio-X Municipal (Perfil de Gestão em {filtro_ano})")

cidade_selecionada = st.selectbox(
    "Digite o nome da cidade para detalhar:",
    options=sorted(df_filtrado['Cidade_UF'].unique()),
    index=None,
    placeholder="Ex: Fortaleza - CE"
)

if cidade_selecionada:
    dados_cidade = df_filtrado[df_filtrado['Cidade_UF'] == cidade_selecionada].iloc[0]
    uf_cidade = dados_cidade['UF']
    media_estado = df_filtrado[df_filtrado['UF'] == uf_cidade].mean(numeric_only=True)
    
    col_radar, col_kpis_cidade = st.columns([1.5, 1])
    
    with col_radar:
        st.subheader("Teia da Gestão (Cidade vs Estado)")
        categorias_dados = [
            'Governança, Eficiência Fiscal e Transparência', 
            'Educação', 
            'Saúde e Bem-Estar', 
            'Infraestrutura e Mobilidade Urbana', 
            'Sustentabilidade', 
            'Desenvolvimento Socioeconômico e Ordem Pública'
        ]
        categorias_labels = ['Governança', 'Educação', 'Saúde', 'Infraestrutura', 'Sustentabilidade', 'Desenv. Socioeconômico']
        
        fig_radar = go.Figure()
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[dados_cidade.get(c, 0) for c in categorias_dados],
            theta=categorias_labels, fill='toself', name=dados_cidade['Cidade'], line_color='#2563EB'
        ))
        
        fig_radar.add_trace(go.Scatterpolar(
            r=[media_estado.get(c, 0) for c in categorias_dados],
            theta=categorias_labels, name=f"Média {uf_cidade}", line_color='#9CA3AF', line=dict(dash='dot')
        ))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), margin=dict(t=20, b=20, l=40, r=40))
        st.plotly_chart(fig_radar, width="stretch")
        
    with col_kpis_cidade:
        st.subheader("Indicadores")
        
        delta_hom = dados_cidade['Taxa_Homicidios_100k'] - media_estado['Taxa_Homicidios_100k']
        st.metric("Taxa de Homicídios", f"{dados_cidade['Taxa_Homicidios_100k']:.2f}", delta=f"{delta_hom:.2f} vs Média UF", delta_color="inverse")
        
        delta_igma = dados_cidade['IGMA'] - media_estado['IGMA']
        st.metric("IGMA Geral", f"{dados_cidade['IGMA']:.2f}", delta=f"{delta_igma:.2f} vs Média UF", delta_color="normal")
        
        delta_desenv = dados_cidade['Desenvolvimento Socioeconômico e Ordem Pública'] - media_estado['Desenvolvimento Socioeconômico e Ordem Pública']
        st.metric("Desenv. Socioeconômico", f"{dados_cidade['Desenvolvimento Socioeconômico e Ordem Pública']:.2f}", delta=f"{delta_desenv:.2f} vs Média UF")
        
        st.caption(f"População: {dados_cidade['Populacao']:,.0f} habitantes")
