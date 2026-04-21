import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
from config_mapas import LINKS_MAPAS
from streamlit_gsheets import GSheetsConnection

# ==========================================
# 1. CONFIGURAÇÃO
# ==========================================
st.set_page_config(
    layout="wide",
    page_title="Monitor de Gestão e Segurança",
    page_icon="🇧🇷",
    initial_sidebar_state="expanded"
)

# ==========================================
# 2. CSS + ESTILIZAÇÃO PREMIUM
# ==========================================
st.markdown("""
<style>
    /* Ajuste de espaçamento geral */
    .block-container { padding-top: 1.5rem; }
    
    /* Título com Gradiente Moderno */
    .gradient-text {
        background: -webkit-linear-gradient(45deg, #3B82F6, #10B981);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
        margin-bottom: 0px;
    }

    /* Animações Suaves */
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(15px);}
        to {opacity: 1; transform: translateY(0);}
    }
    .fade-in { animation: fadeIn 0.6s ease-out forwards; }

    /* Cards de KPI (Estilo Vidro / Dark) */
    .card {
        background: linear-gradient(145deg, #1E293B, #0F172A);
        border: 1px solid #334155;
        padding: 20px;
        border-radius: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        text-align: center;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.2);
        border-color: #3B82F6;
    }
    .kpi-title { font-size: 0.9rem; color: #94A3B8; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-size: 2rem; font-weight: 800; color: #F8FAFC; margin-top: 5px; }

    /* Esconde botões padrões do Streamlit para visual mais limpo */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DADOS (ALTA PERFORMANCE)
# ==========================================
@st.cache_data(ttl=600)
def load_data():
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    # Fazemos o tratamento AQUI DENTRO para o sistema não travar a cada clique
    pilares = [
        'Governança, Eficiência Fiscal e Transparência', 'Educação', 
        'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana', 
        'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública'
    ]
    cols_numericas = ['IGMA', 'Taxa_Homicidios_100k', 'Populacao'] + pilares
    
    for col in cols_numericas:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Cidade' in df.columns and 'UF' in df.columns:
        df['Cidade_Exibicao'] = df['Cidade'] + ' - ' + df['UF']
        
    return df

with st.spinner("⏳ Conectando à base de dados..."):
    try:
        df = load_data()
    except Exception as e:
        st.error(f"Erro ao conectar com o banco de dados: {e}")
        st.stop()

# ==========================================
# 4. SIDEBAR (FILTROS)
# ==========================================
st.sidebar.markdown("### 🎛️ Filtros de Análise")

# Ocultando o menu de Ano na sidebar para dar destaque na tela principal
anos = sorted(df['Ano'].dropna().unique())

with st.sidebar.expander("📍 Localização", expanded=True):
    estados = sorted(df['UF'].dropna().unique())
    filtro_uf = st.multiselect("Selecione os Estados:", estados, placeholder="Todos os estados")

with st.sidebar.expander("👥 Demografia", expanded=True):
    pop_min, pop_max = int(df['Populacao'].min()), int(df['Populacao'].max())
    range_pop = st.slider("Faixa Populacional:", pop_min, pop_max, (pop_min, pop_max), format="%d")

# ==========================================
# 5. CABEÇALHO & LINHA DO TEMPO
# ==========================================
st.markdown('<h1 class="gradient-text fade-in">Monitor: Gestão Pública vs Segurança</h1>', unsafe_allow_html=True)
st.caption("Inteligência de dados sobre o impacto do desenvolvimento na violência municipal.")

st.markdown("<br>", unsafe_allow_html=True)

# Ano na tela principal fica muito mais elegante
col_ano, col_vazia = st.columns([1, 2])
with col_ano:
    filtro_ano = st.selectbox("📅 Selecione o Ano de Referência:", anos, index=len(anos)-1)

# Aplicação dos Filtros
df_filtrado = df[df['Ano'] == filtro_ano].copy()
if filtro_uf:
    df_filtrado = df_filtrado[df_filtrado['UF'].isin(filtro_uf)]
df_filtrado = df_filtrado[(df_filtrado['Populacao'] >= range_pop[0]) & (df_filtrado['Populacao'] <= range_pop[1])]

if df_filtrado.empty:
    st.warning("⚠️ Nenhum dado encontrado com os filtros atuais. Tente expandir a busca.")
    st.stop()

# ==========================================
# 6. CARDS (KPIs)
# ==========================================
def render_kpi(title, value):
    return f"""
    <div class="card fade-in">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3, c4 = st.columns(4)
c1.markdown(render_kpi("Cidades Analisadas", f"{len(df_filtrado):n}".replace(",", ".")), unsafe_allow_html=True)
c2.markdown(render_kpi("Média IGMA", f"{df_filtrado['IGMA'].mean():.2f}".replace(".", ",")), unsafe_allow_html=True)
c3.markdown(render_kpi("Taxa Homicídios", f"{df_filtrado['Taxa_Homicidios_100k'].mean():.2f}".replace(".", ",")), unsafe_allow_html=True)
c4.markdown(render_kpi("População Afetada", f"{df_filtrado['Populacao'].sum():,.0f}".replace(",", ".")), unsafe_allow_html=True)

st.markdown("<br><hr>", unsafe_allow_html=True)

# ==========================================
# 7. GRÁFICO: DISPERSÃO
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.subheader(f"📈 IGMA vs Violência ({filtro_ano})")

fig_scatter = px.scatter(
    df_filtrado, x="IGMA", y="Taxa_Homicidios_100k", color="Regiao",
    size="Populacao", hover_name="Cidade_Exibicao", opacity=0.8,
    color_discrete_sequence=px.colors.qualitative.Pastel # Cores mais vibrantes e suaves
)

fig_scatter.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis_title="Nota IGMA",
    yaxis_title="Homicídios (por 100k)",
    height=450,
    margin=dict(t=10, b=10, l=10, r=10)
)
st.plotly_chart(fig_scatter, use_container_width=True)
st.markdown('</div><hr>', unsafe_allow_html=True)

# ==========================================
# 8. MAPAS
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.subheader("🗺️ Panorama Geográfico")

col_esc, col_uf, col_tema = st.columns([1, 1, 2])
with col_esc:
    escopo = st.radio("Visão:", ["Brasil", "Por Estado"])
with col_uf:
    uf_mapa = st.selectbox("Estado:", sorted(df['UF'].unique())) if escopo == "Por Estado" else "Brasil"
with col_tema:
    tema_mapa = st.radio("Tema de Análise:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], horizontal=True)

# Lógica Corrigida de URL
url = ""
try:
    url = LINKS_MAPAS.get(filtro_ano, {}).get(uf_mapa, {}).get(tema_mapa, "")
except Exception:
    pass

if url and "SEU_LINK" not in url:
    with st.spinner("Carregando mapa interativo..."):
        components.iframe(url, height=700, scrolling=False)
else:
    st.info(f"📍 O mapa detalhado para **{uf_mapa}** ({tema_mapa}) ainda não está configurado.")

st.markdown('</div><hr>', unsafe_allow_html=True)

# ==========================================
# 9. RAIO-X MUNICIPAL (RADAR)
# ==========================================
st.markdown('<div class="fade-in">', unsafe_allow_html=True)
st.subheader("🔎 Perfil de Gestão Municipal")

cidade = st.selectbox("Pesquise a cidade:", sorted(df_filtrado['Cidade_Exibicao'].dropna().unique()), index=None, placeholder="Digite o nome do município...")

if cidade:
    dados = df_filtrado[df_filtrado['Cidade_Exibicao'] == cidade].iloc[0]
    categorias_reais = [
        'Governança, Eficiência Fiscal e Transparência', 'Educação',
        'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana',
        'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública'
    ]
    labels_radar = ['Governança', 'Educação', 'Saúde', 'Infraestrutura', 'Sustent.', 'Desenv. Econ.']

    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=[dados.get(c, 0) for c in categorias_reais],
        theta=labels_radar,
        fill='toself',
        name=cidade,
        line_color='#10B981', # Verde esmeralda moderno
        fillcolor='rgba(16, 185, 129, 0.4)'
    ))

    fig_radar.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], gridcolor='#334155', tickfont=dict(color='#94A3B8')),
            angularaxis=dict(gridcolor='#334155')
        ),
        margin=dict(t=30, b=30, l=40, r=40),
        height=450
    )
    
    col_vazia_esq, col_grafico, col_vazia_dir = st.columns([1, 2, 1])
    with col_grafico:
        st.plotly_chart(fig_radar, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
