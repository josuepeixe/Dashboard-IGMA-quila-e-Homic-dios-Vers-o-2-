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
    size="Populacao", hover_name="Cidade_Exibicao", opacity=0.9,
    color_discrete_sequence=px.colors.qualitative.Set1, # Cores mais fortes e vibrantes
    size_max=45 # Aumenta o tamanho máximo das bolinhas
)

# Adiciona um contorno branco/cinza nas bolinhas para dar destaque no fundo
fig_scatter.update_traces(marker=dict(line=dict(width=1, color='#E2E8F0')))

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
st.subheader("🗺️ Panorama Geográfico")

m1, m2, m3, m4 = st.columns([1, 1, 1.5, 1.5])
with m1: escopo = st.radio("Nível:", ["Brasil", "Estado"])
with m2: uf_mapa = st.selectbox("UF:", sorted(df['UF'].unique())) if escopo == "Estado" else "Brasil"
with m3: tema_mapa = st.radio("Tema:", ["Violência (Homicídios)", "Gestão Pública (IGMA)"], horizontal=True)
with m4:
    if tema_mapa == "Gestão Pública (IGMA)":
        pilar = st.selectbox("Pilar:", ["IGMA Geral", "Desenvolvimento Socioeconômico e Ordem Pública"])
    else:
        pilar = None

# Busca URL com tratamento para evitar o erro TypeError
url = ""
try:
    dados_ano = LINKS_MAPAS.get(filtro_ano, {})
    dados_local = dados_ano.get(uf_mapa, {})
    
    if tema_mapa == "Violência (Homicídios)":
        url = dados_local.get(tema_mapa, "")
    else:
        url = dados_local.get(tema_mapa, {}).get(pilar, "")
except Exception:
    url = ""

if isinstance(url, str) and url.startswith("http"):
    components.iframe(url, height=800)
else:
    st.info(f"🔗 Mapa não configurado para {uf_mapa} / {tema_mapa}")

st.divider()

# ==========================================
# 9. RAIO-X MUNICIPAL (RADAR)
# ==========================================
st.subheader("🔎 Raio-X Municipal")

cidade_sel = st.selectbox("Selecione a Cidade:", sorted(df_filtrado['Cidade_Exibicao'].unique()), index=None)

if cidade_sel:
    dados_cid = df_filtrado[df_filtrado['Cidade_Exibicao'] == cidade_sel].iloc[0]
    uf_cid = dados_cid['UF']
    medias_uf = df_filtrado[df_filtrado['UF'] == uf_cid].mean(numeric_only=True)

    r1, r2 = st.columns([1.5, 1])
    
    with r1:
        st.write(f"**Teia de Desempenho: {cidade_sel}**")
        pilares_radar = [
            'Governança, Eficiência Fiscal e Transparência', 'Educação',
            'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana',
            'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública'
        ]
        labels = ['Gov', 'Edu', 'Saúde', 'Infra', 'Sust', 'Desenv']
        
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=[dados_cid[p] for p in pilares_radar], theta=labels, fill='toself', name=dados_cid['Cidade'], line_color='#10B981'
        ))
        fig_radar.add_trace(go.Scatterpolar(
            r=[medias_uf[p] for p in pilares_radar], theta=labels, name=f"Média {uf_cid}", line=dict(dash='dot'), line_color='white'
        ))
        fig_radar.update_layout(template="plotly_dark", polar=dict(radialaxis=dict(visible=True, range=[0, 100])), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_radar, use_container_width=True)

    with r2:
        st.write("**Comparativo Numérico**")
        
        # Métrica de Homicídios (Menor é melhor -> Delta Inverso)
        delta_h = dados_cid['Taxa_Homicidios_100k'] - medias_uf['Taxa_Homicidios_100k']
        st.metric("Taxa de Homicídios", f"{dados_cid['Taxa_Homicidios_100k']:.2f}", 
                  delta=f"{delta_h:.2f} vs Estado", delta_color="inverse")
        
        # Métrica de IGMA (Maior é melhor)
        delta_i = dados_cid['IGMA'] - medias_uf['IGMA']
        st.metric("Nota IGMA", f"{dados_cid['IGMA']:.2f}", 
                  delta=f"{delta_i:.2f} vs Estado")
        
        st.markdown(f"""
        **Detalhes Adicionais:**
        - **População:** {dados_cid['Populacao']:,.0f} hab.
        - **Região:** {dados_cid['Regiao']}
        - **Status IGMA:** {dados_cid['Class__IGMA']}
        """)
