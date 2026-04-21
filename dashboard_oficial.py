import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from config_mapas import LINKS_MAPAS
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
# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    # Conexão segura com Google Sheets via Secrets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    # Pilares do IGMA
    pilares = [
        'Governança, Eficiência Fiscal e Transparência', 
        'Educação', 
        'Saúde e Bem-Estar', 
        'Infraestrutura e Mobilidade Urbana', 
        'Sustentabilidade', 
        'Desenvolvimento Socioeconômico e Ordem Pública'
    ]
    
    # Tratamento de Colunas Numéricas
    cols_numericas = ['IGMA', 'Taxa_Homicidios_100k', 'Populacao'] + pilares
    for col in cols_numericas:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Criação da coluna de exibição para evitar erro com cidades de mesmo nome
    if 'Cidade' in df.columns and 'UF' in df.columns:
        df['Cidade_Exibicao'] = df['Cidade'] + ' - ' + df['UF']
            
    return df

# Tenta carregar os dados com tratamento de erro global
try:
    df = load_data()
except Exception as e:
    st.error(f"⚠️ Erro ao conectar com o Google Sheets. Verifique seus 'Secrets'. Detalhes: {e}")
    st.stop()

# ==========================================
# 3. SIDEBAR (FILTROS)
# ==========================================
st.sidebar.header("🔍 Filtros Globais")

# Filtro de Ano
anos_disponiveis = sorted(df['Ano'].dropna().unique())
filtro_ano = st.sidebar.selectbox("Selecione o Ano:", anos_disponiveis, index=len(anos_disponiveis)-1)

# Filtro de Estado
estados_disponiveis = sorted(df['UF'].dropna().unique())
filtro_uf = st.sidebar.multiselect("Filtrar por Estado(s):", estados_disponiveis)

# Filtro de População
pop_min, pop_max = int(df['Populacao'].min()), int(df['Populacao'].max())
range_pop = st.sidebar.slider("Faixa Populacional:", pop_min, pop_max, (pop_min, pop_max))

# Aplicação dos Filtros
df_filtrado = df[df['Ano'] == filtro_ano].copy()
if filtro_uf:
    df_filtrado = df_filtrado[df_filtrado['UF'].isin(filtro_uf)]
df_filtrado = df_filtrado[(df_filtrado['Populacao'] >= range_pop[0]) & (df_filtrado['Populacao'] <= range_pop[1])]

# Se o filtro resultar em nada, avisa o usuário e para
if df_filtrado.empty:
    st.warning("Nenhum município encontrado com estes filtros. Ajuste a população ou o estado.")
    st.stop()

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
# BLOCO 1: KPIs (MÉTRICAS)
# ==========================================
st.title("🇧🇷 Monitor: Gestão Pública vs. Segurança")
st.markdown("Análise do impacto do desenvolvimento municipal na violência letal.")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Cidades Analisadas", f"{len(df_filtrado):n}".replace(",", "."))
col2.metric("Média IGMA", f"{df_filtrado['IGMA'].mean():.2f}".replace(".", ","))
col3.metric("Média Homicídios (100k)", f"{df_filtrado['Taxa_Homicidios_100k'].mean():.2f}".replace(".", ","))
col4.metric("População Total", f"{df_filtrado['Populacao'].sum():,.0f}".replace(",", "."))

st.markdown("---")

# ==========================================
# BLOCO 2: DISPERSÃO (CORRELAÇÃO)
# ==========================================
st.header(f"📈 Correlação: Violência vs. IGMA ({filtro_ano})")

col_tit, col_foco = st.columns([3, 1])
with col_foco:
    opcoes_regiao = ["Todas as Regiões"] + sorted(df_filtrado['Regiao'].dropna().unique())
    foco_regiao = st.selectbox("Destacar Região:", options=opcoes_regiao)

fig_scatter = go.Figure()

if foco_regiao == "Todas as Regiões":
    fig_scatter = px.scatter(
        df_filtrado, x="IGMA", y="Taxa_Homicidios_100k", color="Regiao",
        size="Populacao", hover_name="Cidade_Exibicao", opacity=0.7,
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
        name=foco_regiao, text=df_foco['Cidade_Exibicao'],
        hovertemplate="<b>%{text}</b><br>IGMA: %{x:.2f}<br>Homicídios: %{y:.2f}<extra></extra>"
    ))

fig_scatter.update_layout(
    xaxis_title="Nota IGMA Geral", yaxis_title="Taxa de Homicídios (por 100k)",
    height=500, margin=dict(t=30, b=0), legend_title_text="Região"
)
st.plotly_chart(fig_scatter, use_container_width=True)

st.markdown("---")

# ==========================================
# BLOCO 3: MAPAS (IFRAME)
# ==========================================
st.header("🗺️ Panorama Geográfico")

col_escopo, col_uf_mapa, col_tema, col_pilar = st.columns([1, 1, 1.2, 1.5])

with col_escopo:
    escopo = st.radio("1. Nível:", ["Brasil", "Por Estado"], key="radio_escopo")

with col_uf_mapa:
    if escopo == "Por Estado":
        lista_ufs = sorted(df['UF'].unique())
        index_padrao = lista_ufs.index("CE") if "CE" in lista_ufs else 0
        uf_escolhida = st.selectbox("2. Escolha a UF:", lista_ufs, index=index_padrao)
    else:
        uf_escolhida = "Brasil"
        st.write("") 

with col_tema:
    tema = st.radio("3. Tema:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], key="radio_tema")

with col_pilar:
    if tema == "Gestão Pública (IGMA)":
        pilar_escolhido = st.selectbox("4. Pilar:", ["IGMA Geral", "Desenvolvimento Socioeconômico e Ordem Pública"])
    else:
        st.info(f"Homicídios em {filtro_ano}.")

# Busca da URL do Mapa
url_mapa = ""
try:
    dict_ano = LINKS_MAPAS.get(filtro_ano, {})
    dict_local = dict_ano.get(uf_escolhida, {})
    
    if tema == "Violência (Homicídios)":
        url_mapa = dict_local.get(tema, "")
    else:
        url_mapa = dict_local.get(tema, {}).get(pilar_escolhido, "")
except Exception:
    url_mapa = ""

if url_mapa and "SEU_LINK" not in url_mapa:
    components.iframe(url_mapa, height=850, scrolling=False)
else:
    st.warning(f"🔗 Mapa indisponível para {uf_escolhida} em {filtro_ano}.")

st.markdown("---")

# ==========================================
# BLOCO 4: RAIO-X MUNICIPAL (RADAR)
# ==========================================
st.header(f"🔎 Raio-X Municipal ({filtro_ano})")

cidade_selecionada = st.selectbox(
    "Selecione a cidade:",
    options=sorted(df_filtrado['Cidade_Exibicao'].dropna().unique()),
    index=None,
    placeholder="Ex: Fortaleza - CE"
)

if cidade_selecionada:
    dados_cidade = df_filtrado[df_filtrado['Cidade_Exibicao'] == cidade_selecionada].iloc[0]
    uf_cidade = dados_cidade['UF']
    media_estado = df_filtrado[df_filtrado['UF'] == uf_cidade].mean(numeric_only=True)
    
    col_radar, col_kpis_cidade = st.columns([1.5, 1])
    
    with col_radar:
        st.subheader("Teia da Gestão (Cidade vs Média Estado)")
        categorias_dados = [
            'Governança, Eficiência Fiscal e Transparência', 'Educação', 
            'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana', 
            'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública'
        ]
        categorias_labels = ['Governança', 'Educação', 'Saúde', 'Infraestrutura', 'Sustentabilidade', 'Desenvolvimento']
        
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
        st.plotly_chart(fig_radar, use_container_width=True)
        
    with col_kpis_cidade:
        st.subheader("Indicadores")
        
        delta_hom = dados_cidade['Taxa_Homicidios_100k'] - media_estado['Taxa_Homicidios_100k']
        st.metric("Taxa de Homicídios", f"{dados_cidade['Taxa_Homicidios_100k']:.2f}", delta=f"{delta_hom:.2f} vs Média UF", delta_color="inverse")
        
        delta_igma = dados_cidade['IGMA'] - media_estado['IGMA']
        st.metric("IGMA Geral", f"{dados_cidade['IGMA']:.2f}", delta=f"{delta_igma:.2f} vs Média UF")
        
        st.caption(f"População: {dados_cidade['Populacao']:,.0f} hab.")
