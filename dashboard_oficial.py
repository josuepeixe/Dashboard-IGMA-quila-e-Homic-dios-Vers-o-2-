import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from config_mapas import LINKS_MAPAS
from streamlit_gsheets import GSheetsConnection

# ==========================================
# CONFIG
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Monitor de Gestão e Segurança",
    page_icon="🇧🇷"
)

# ==========================================
# CSS + ANIMAÇÕES
# ==========================================
st.markdown("""
<style>

.block-container {
    padding-top: 2rem;
}

/* ===== ANIMAÇÃO ===== */
@keyframes fadeIn {
    from {opacity: 0; transform: translateY(10px);}
    to {opacity: 1; transform: translateY(0);}
}

.fade-in {
    animation: fadeIn 0.6s ease-in-out;
}

/* ===== CARDS ===== */
.card {
    background-color: #161B22;
    padding: 18px;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    transition: all 0.25s ease;
}

.card:hover {
    transform: translateY(-4px) scale(1.01);
    box-shadow: 0 8px 20px rgba(0,0,0,0.5);
}

/* ===== KPI ===== */
.kpi {
    text-align: center;
}

.kpi-title {
    font-size: 13px;
    color: #9CA3AF;
}

.kpi-value {
    font-size: 26px;
    font-weight: bold;
    transition: transform 0.2s ease;
}

.card:hover .kpi-value {
    transform: scale(1.05);
}

/* ===== SIDEBAR ===== */
section[data-testid="stSidebar"] {
    animation: fadeIn 0.8s ease;
}

/* ===== TÍTULOS ===== */
h1, h2, h3 {
    animation: fadeIn 0.5s ease;
}

/* ===== ELEMENTOS ===== */
.element-container {
    animation: fadeIn 0.7s ease;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# DATA
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    return conn.read()

with st.spinner("Carregando dados..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erro ao conectar: {e}")
        st.stop()

# ==========================================
# TRATAMENTO
# ==========================================
pilares = [
    'Governança, Eficiência Fiscal e Transparência', 
    'Educação', 
    'Saúde e Bem-Estar', 
    'Infraestrutura e Mobilidade Urbana', 
    'Sustentabilidade', 
    'Desenvolvimento Socioeconômico e Ordem Pública'
]

cols_numericas = ['IGMA', 'Taxa_Homicidios_100k', 'Populacao'] + pilares

for col in cols_numericas:
    if col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.replace(',', '.')
        df[col] = pd.to_numeric(df[col], errors='coerce')

df['Cidade_Exibicao'] = df['Cidade'] + ' - ' + df['UF']

# ==========================================
# SIDEBAR
# ==========================================
st.sidebar.markdown("## 🔍 Filtros")

with st.sidebar.expander("Ano", True):
    anos = sorted(df['Ano'].dropna().unique())
    filtro_ano = st.selectbox("Ano", anos, index=len(anos)-1)

with st.sidebar.expander("Localização"):
    estados = sorted(df['UF'].dropna().unique())
    filtro_uf = st.multiselect("Estados", estados)

with st.sidebar.expander("População"):
    pop_min, pop_max = int(df['Populacao'].min()), int(df['Populacao'].max())
    range_pop = st.slider("Faixa", pop_min, pop_max, (pop_min, pop_max))

# ==========================================
# FILTRO
# ==========================================
df_filtrado = df[df['Ano'] == filtro_ano].copy()

if filtro_uf:
    df_filtrado = df_filtrado[df_filtrado['UF'].isin(filtro_uf)]

df_filtrado = df_filtrado[
    (df_filtrado['Populacao'] >= range_pop[0]) &
    (df_filtrado['Populacao'] <= range_pop[1])
]

if df_filtrado.empty:
    st.warning("Sem dados com esses filtros.")
    st.stop()

# ==========================================
# HEADER
# ==========================================
st.title("🇧🇷 Monitor: Gestão Pública vs Segurança")
st.caption("Impacto do desenvolvimento municipal na violência")

# ==========================================
# KPI
# ==========================================
def kpi(title, value):
    st.markdown(f"""
    <div class="card kpi fade-in">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    kpi("Cidades", f"{len(df_filtrado):n}".replace(",", "."))

with col2:
    kpi("Média IGMA", f"{df_filtrado['IGMA'].mean():.2f}".replace(".", ","))

with col3:
    kpi("Homicídios (100k)", f"{df_filtrado['Taxa_Homicidios_100k'].mean():.2f}".replace(".", ","))

with col4:
    kpi("População", f"{df_filtrado['Populacao'].sum():,.0f}".replace(",", "."))

st.divider()

# ==========================================
# SCATTER
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)

st.subheader("📈 Correlação IGMA vs Violência")

fig = px.scatter(
    df_filtrado,
    x="IGMA",
    y="Taxa_Homicidios_100k",
    color="Regiao",
    size="Populacao",
    hover_name="Cidade_Exibicao",
    opacity=0.7
)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    transition=dict(duration=500),
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# MAPA
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)

st.subheader("🗺️ Mapa")

col1, col2, col3 = st.columns(3)

with col1:
    escopo = st.radio("Nível", ["Brasil", "Estado"])

with col2:
    if escopo == "Estado":
        uf = st.selectbox("UF", sorted(df['UF'].unique()))
    else:
        uf = "Brasil"

with col3:
    tema = st.radio("Tema", ["Violência", "IGMA"])

url = LINKS_MAPAS.get(filtro_ano, {}).get(uf, {}).get("Violência (Homicídios)", "")

if url:
    components.iframe(url, height=900)
else:
    st.info("Mapa indisponível")

st.markdown('</div>', unsafe_allow_html=True)

st.divider()

# ==========================================
# RADAR
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)

st.subheader("🔎 Raio-X Municipal")

cidade = st.selectbox(
    "Cidade",
    sorted(df_filtrado['Cidade_Exibicao'].dropna().unique()),
    index=None
)

if cidade:
    dados = df_filtrado[df_filtrado['Cidade_Exibicao'] == cidade].iloc[0]

    categorias = [
        'Governança, Eficiência Fiscal e Transparência',
        'Educação',
        'Saúde e Bem-Estar',
        'Infraestrutura e Mobilidade Urbana',
        'Sustentabilidade',
        'Desenvolvimento Socioeconômico e Ordem Pública'
    ]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[dados[c] for c in categorias],
        theta=['Gov', 'Edu', 'Saúde', 'Infra', 'Sust', 'Desenv'],
        fill='toself'
    ))

    fig.update_layout(
        template="plotly_dark",
        transition=dict(duration=500)
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
