import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
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

df_f = df[df['Ano'] == ano_sel].copy()
if uf_sel:
    df_f = df_f[df_f['UF'].isin(uf_sel)]

with c3:
    cidades_lista = sorted(df_f['Cidade_Exibicao'].dropna().unique())
    cidade_destaque = st.selectbox("🎯 Localizar Município Específico:", cidades_lista, index=None, placeholder="Digite o nome da cidade...")

if df_f.empty:
    st.warning("Nenhum dado encontrado para essa seleção.")
    st.stop()

# 3. Cálculo das Médias
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

fig.update_traces(marker=dict(line=dict(width=1, color='Gray')))
fig.add_hline(y=media_hom, line_dash="dot", line_color="#EF4444", annotation_text=f"Média Homicídios ({media_hom:.1f})", annotation_position="top left")
fig.add_vline(x=media_igma, line_dash="dot", line_color="#10B981", annotation_text=f"Média IGMA ({media_igma:.1f})", annotation_position="top right")

# 5. Lógica do Destaque (Mira)
if cidade_destaque:
    dados_dest = df_f[df_f['Cidade_Exibicao'] == cidade_destaque].iloc[0]
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

fig.update_layout(
    xaxis_title="Nota IGMA Geral", 
    yaxis_title="Taxa de Homicídios (por 100k)",
    margin=dict(t=30, b=30, l=30, r=30),
    height=550
)

st.plotly_chart(fig, use_container_width=True, theme="streamlit")
st.divider()

# ==========================================
# 7. RESUMO ANALÍTICO EM ABAS
# ==========================================
st.markdown("### 📊 Painel de Análise Detalhada")

# Criando as abas de análise
tab_extremos, tab_capitais, tab_regioes = st.tabs(["🏆 Extremos da Matriz", "🏛️ Comparativo de Capitais", "🌎 Médias por Região"])

# --- ABA 1: EXTREMOS (O TOP 5) ---
with tab_extremos:
    col_rank1, col_rank2 = st.columns(2)
    with col_rank1:
        st.markdown("#### 🟢 Zona Ideal (Alto IGMA, Baixa Violência)")
        zona_ideal = df_f[(df_f['IGMA'] > media_igma) & (df_f['Taxa_Homicidios_100k'] < media_hom)]
        if not zona_ideal.empty:
            top5_ideal = zona_ideal.sort_values(by=['Taxa_Homicidios_100k', 'IGMA'], ascending=[True, False]).head(5)
            st.dataframe(top5_ideal[['Cidade', 'UF', 'IGMA', 'Taxa_Homicidios_100k']], hide_index=True, use_container_width=True)
        else:
            st.info("Nenhuma cidade atingiu a zona ideal nesta seleção.")

    with col_rank2:
        st.markdown("#### 🔴 Zona Crítica (Baixo IGMA, Alta Violência)")
        zona_critica = df_f[(df_f['IGMA'] < media_igma) & (df_f['Taxa_Homicidios_100k'] > media_hom)]
        if not zona_critica.empty:
            top5_critica = zona_critica.sort_values(by=['Taxa_Homicidios_100k', 'IGMA'], ascending=[False, True]).head(5)
            st.dataframe(top5_critica[['Cidade', 'UF', 'IGMA', 'Taxa_Homicidios_100k']], hide_index=True, use_container_width=True)
        else:
            st.info("Nenhuma cidade está na zona crítica nesta seleção.")

# --- ABA 2: CAPITAIS ---
with tab_capitais:
    # Lista com todas as capitais no formato que criamos na coluna Cidade_Exibicao
    lista_capitais = [
        "Aracaju - SE", "Belém - PA", "Belo Horizonte - MG", "Boa Vista - RR", "Brasília - DF",
        "Campo Grande - MS", "Cuiabá - MT", "Curitiba - PR", "Florianópolis - SC", "Fortaleza - CE",
        "Goiânia - GO", "João Pessoa - PB", "Macapá - AP", "Maceió - AL", "Manaus - AM",
        "Natal - RN", "Palmas - TO", "Porto Alegre - RS", "Porto Velho - RO", "Recife - PE",
        "Rio Branco - AC", "Rio de Janeiro - RJ", "Salvador - BA", "São Luís - MA",
        "São Paulo - SP", "Teresina - PI", "Vitória - ES"
    ]
    
    df_capitais = df_f[df_f['Cidade_Exibicao'].isin(lista_capitais)].copy()
    
    if not df_capitais.empty:
        # Ordenamos por IGMA (do melhor para o pior)
        df_capitais = df_capitais.sort_values(by='IGMA', ascending=False)
        st.dataframe(
            df_capitais[['Cidade_Exibicao', 'Regiao', 'IGMA', 'Taxa_Homicidios_100k', 'Populacao']],
            column_config={
                "Cidade_Exibicao": "Capital",
                "Taxa_Homicidios_100k": st.column_config.NumberColumn("Homicídios (100k)", format="%.2f"),
                "IGMA": st.column_config.NumberColumn("Nota IGMA", format="%.2f"),
                "Populacao": st.column_config.NumberColumn("População", format="%d")
            },
            hide_index=True, use_container_width=True
        )
    else:
        st.info("Nenhuma capital encontrada para o filtro atual.")

# --- ABA 3: REGIÕES ---
with tab_regioes:
    # Agrupamos os dados pela coluna 'Regiao', calculando a média para as taxas e a soma para a população
    df_regioes = df_f.groupby('Regiao').agg(
        Cidades=('Cidade', 'count'),
        IGMA=('IGMA', 'mean'),
        Taxa_Homicidios_100k=('Taxa_Homicidios_100k', 'mean'),
        Populacao=('Populacao', 'sum')
    ).reset_index()
    
    # Ordenamos pela média do IGMA
    df_regioes = df_regioes.sort_values(by='IGMA', ascending=False)
    
    st.dataframe(
        df_regioes,
        column_config={
            "Regiao": "Região do Brasil",
            "Cidades": "Qtd. Cidades Analisadas",
            "IGMA": st.column_config.NumberColumn("Média IGMA", format="%.2f"),
            "Taxa_Homicidios_100k": st.column_config.NumberColumn("Média Homicídios (100k)", format="%.2f"),
            "Populacao": st.column_config.NumberColumn("População Total (hab)", format="%d")
        },
        hide_index=True, use_container_width=True
    )
