import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from utils import load_data, aplicar_estilo_comum

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Correlação e Matriz")
aplicar_estilo_comum()

df = load_data()

st.markdown('<h1 class="gradient-text">📈 Matriz de Desempenho</h1>', unsafe_allow_html=True)
st.caption("Cruze os dados para identificar as zonas críticas e ideais dos municípios brasileiros.")

# 2. Filtros Dinâmicos
c1, c2, c3 = st.columns([1, 1.5, 2])
with c1:
    ano_sel = st.selectbox("Ano:", sorted(df['Ano'].dropna().unique(), reverse=True))

with c2:
    ufs = sorted(df['UF'].dropna().unique())
    uf_sel = st.multiselect("Filtrar por Estado:", ufs, placeholder="Todos os Estados")

# Filtra primeiro o ano e estado para alimentar o próximo filtro
df_f = df[df['Ano'] == ano_sel].copy()
if uf_sel:
    df_f = df_f[df_f['UF'].isin(uf_sel)]

with c3:
    # A Busca por Município fica muito mais inteligente se procurar apenas no estado selecionado
    cidades_lista = sorted(df_f['Cidade_Exibicao'].dropna().unique())
    cidade_destaque = st.selectbox("🎯 Localizar Município Específico:", cidades_lista, index=None, placeholder="Digite o nome da cidade...")

if df_f.empty:
    st.warning("Nenhum dado encontrado para essa seleção.")
    st.stop()

# 3. Cálculo das Médias (O coração da Matriz)
media_igma = df_f['IGMA'].mean()
media_hom = df_f['Taxa_Homicidios_100k'].mean()

st.markdown("<br>", unsafe_allow_html=True)

# 4. Construção do Gráfico
fig = px.scatter(
    df_f, x="IGMA", y="Taxa_Homicidios_100k", color="Regiao",
    size="Populacao", hover_name="Cidade_Exibicao",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    size_max=35, opacity=0.8
)

# Adiciona o contorno sutil em todas as bolinhas normais
fig.update_traces(marker=dict(line=dict(width=1, color='Gray')))

# Desenhando a Matriz de Quadrantes (Linhas tracejadas)
fig.add_hline(y=media_hom, line_dash="dot", line_color="#EF4444", annotation_text=f"Média Homicídios ({media_hom:.1f})", annotation_position="top left")
fig.add_vline(x=media_igma, line_dash="dot", line_color="#10B981", annotation_text=f"Média IGMA ({media_igma:.1f})", annotation_position="top right")

# 5. Lógica do Destaque (Mira)
if cidade_destaque:
    dados_dest = df_f[df_f['Cidade_Exibicao'] == cidade_destaque].iloc[0]
    
    # Adiciona uma camada extra por cima com o município destacado
    fig.add_trace(go.Scatter(
        x=[dados_dest['IGMA']], 
        y=[dados_dest['Taxa_Homicidios_100k']],
        mode='markers+text',
        marker=dict(size=20, color='#F59E0B', line=dict(width=3, color='white')),
        text=[f"📍 {cidade_destaque}"], 
        textposition="top center",
        textfont=dict(size=14, color='white' if st.get_option('theme.base') == 'dark' else 'black'),
        name="Destaque",
        showlegend=False
    ))

# 6. Configuração Final do Layout
fig.update_layout(
    xaxis_title="Nota IGMA Geral", 
    yaxis_title="Taxa de Homicídios (por 100k)",
    margin=dict(t=30, b=30, l=30, r=30),
    height=550
)

# Exibe o gráfico adaptando o tema claro/escuro
st.plotly_chart(fig, use_container_width=True, theme="streamlit")
st.divider()

# 7. Resumo Analítico (Top 5)
st.markdown("### 🏆 Extremos da Matriz")
col_rank1, col_rank2 = st.columns(2)

with col_rank1:
    st.markdown("#### 🟢 Zona Ideal (Alto IGMA, Baixa Violência)")
    st.caption("Cidades com Gestão acima da média e Homicídios abaixo da média.")
    
    # Filtra o quadrante inferior direito
    zona_ideal = df_f[(df_f['IGMA'] > media_igma) & (df_f['Taxa_Homicidios_100k'] < media_hom)]
    
    if not zona_ideal.empty:
        # Ordena para pegar as melhores das melhores
        top5_ideal = zona_ideal.sort_values(by=['Taxa_Homicidios_100k', 'IGMA'], ascending=[True, False]).head(5)
        st.dataframe(
            top5_ideal[['Cidade', 'UF', 'IGMA', 'Taxa_Homicidios_100k']],
            column_config={
                "IGMA": st.column_config.NumberColumn(format="%.2f"),
                "Taxa_Homicidios_100k": st.column_config.NumberColumn("Homicídios (100k)", format="%.2f")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("Nenhuma cidade atingiu a zona ideal nesta seleção.")

with col_rank2:
    st.markdown("#### 🔴 Zona Crítica (Baixo IGMA, Alta Violência)")
    st.caption("Cidades com Gestão abaixo da média e Homicídios acima da média.")
    
    # Filtra o quadrante superior esquerdo
    zona_critica = df_f[(df_f['IGMA'] < media_igma) & (df_f['Taxa_Homicidios_100k'] > media_hom)]
    
    if not zona_critica.empty:
        # Ordena para pegar as mais críticas
        top5_critica = zona_critica.sort_values(by=['Taxa_Homicidios_100k', 'IGMA'], ascending=[False, True]).head(5)
        st.dataframe(
            top5_critica[['Cidade', 'UF', 'IGMA', 'Taxa_Homicidios_100k']],
            column_config={
                "IGMA": st.column_config.NumberColumn(format="%.2f"),
                "Taxa_Homicidios_100k": st.column_config.NumberColumn("Homicídios (100k)", format="%.2f")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("Nenhuma cidade está na zona crítica nesta seleção.")
