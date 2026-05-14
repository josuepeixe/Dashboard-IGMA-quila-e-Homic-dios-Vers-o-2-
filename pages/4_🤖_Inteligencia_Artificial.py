import streamlit as st
import plotly.express as px
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from utils import load_data, aplicar_estilo_comum
from sklearn.metrics import r2_score

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="Inteligência Artificial & Correlação")
aplicar_estilo_comum()

df = load_data()

st.markdown('<h1 class="gradient-text">🤖 IA e Correlação Profunda</h1>', unsafe_allow_html=True)
st.caption("Descubra os padrões ocultos nos dados usando algoritmos de Machine Learning e estatística avançada.")

# 2. Filtros Dinâmicos (Para treinar a IA em recortes específicos)
c1, c2 = st.columns([1, 2])
with c1:
    ano_sel = st.selectbox("Treinar modelo com dados do Ano:", sorted(df['Ano'].dropna().unique(), reverse=True))
with c2:
    ufs = sorted(df['UF'].dropna().unique())
    uf_sel = st.multiselect("Filtrar por Estado (Deixe vazio para o Brasil todo):", ufs)

df_f = df[df['Ano'] == ano_sel].copy()
if uf_sel:
    df_f = df_f[df_f['UF'].isin(uf_sel)]

# Pilares que serão analisados
pilares = [
    'Governança, Eficiência Fiscal e Transparência', 
    'Educação', 'Saúde e Bem-Estar', 
    'Infraestrutura e Mobilidade Urbana', 
    'Sustentabilidade', 
    'Desenvolvimento Socioeconômico e Ordem Pública'
]

# Removemos linhas vazias para o algoritmo de IA não falhar
df_ml = df_f.dropna(subset=pilares + ['Taxa_Homicidios_100k'])

if len(df_ml) < 10:
    st.error("⚠️ Dados insuficientes para treinar a Inteligência Artificial neste recorte. Tente selecionar mais estados ou o Brasil todo.")
    st.stop()

st.divider()

# Criando Abas para separar a IA da Estatística Clássica
tab_ia, tab_corr = st.tabs(["🧠 O Peso dos Pilares (Machine Learning)", "📊 Matriz de Correlação Global"])

# ==========================================
# ABA 1: MACHINE LEARNING (RANDOM FOREST)
# ==========================================
with tab_ia:
    st.markdown("### Qual área da Gestão Pública mais impacta a Segurança?")
    st.caption("O algoritmo analisou todas as cidades e ranqueou o grau de importância de cada pilar para a Taxa de Homicídios.")

    # Treinando o Modelo
    X = df_ml[pilares]
    y = df_ml['Taxa_Homicidios_100k']

    modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo_rf.fit(X, y)

    # Pegando as previsões da IA para comparar com a realidade
    y_previsto = modelo_rf.predict(X)
    
    # Calculando a Nota de Aprendizado (R²)
    from sklearn.metrics import r2_score
    acuracia = r2_score(y, y_previsto) * 100

    c_grafico, c_metricas = st.columns([2, 1])

    with c_grafico:
        # Gráfico de Barras dos Pesos (O que já tínhamos feito)
        importancias = modelo_rf.feature_importances_
        df_importancia = pd.DataFrame({'Pilar': pilares, 'Impacto (%)': importancias * 100}).sort_values(by='Impacto (%)', ascending=True)
        
        fig_ia = px.bar(df_importancia, x='Impacto (%)', y='Pilar', orientation='h', color='Impacto (%)', color_continuous_scale=px.colors.sequential.Tealgrn, text_auto='.1f')
        fig_ia.update_layout(xaxis_title="Grau de Influência no Modelo IA (%)", yaxis_title="", height=400, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig_ia, use_container_width=True, theme="streamlit")

    with c_metricas:
        # 1. Métrica de Confiabilidade
        st.markdown("#### 🧠 Desempenho da IA")
        st.metric("Confiabilidade do Modelo (R²)", f"{acuracia:.1f}%")
        st.caption("Um R² alto indica que a IA conseguiu aprender os padrões reais entre a gestão e a violência.")
        st.divider()
        
        # 2. Gráfico de Dispersão: Real vs Previsto (A Prova do Aprendizado)
        df_prova = pd.DataFrame({'Real': y, 'Previsto': y_previsto})
        fig_prova = px.scatter(df_prova, x='Real', y='Previsto', opacity=0.6, color_discrete_sequence=['#F59E0B'], title="Real vs Previsto")
        # Linha perfeita (onde a IA acerta na mosca)
        max_val = max(df_prova['Real'].max(), df_prova['Previsto'].max())
        fig_prova.add_shape(type="line", x0=0, y0=0, x1=max_val, y1=max_val, line=dict(color="white", dash="dot"))
        
        fig_prova.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Homicídios Reais", yaxis_title="Previsão da IA")
        st.plotly_chart(fig_prova, use_container_width=True, theme="streamlit")
    
    st.info("💡 **Como ler este gráfico:** O pilar com o maior percentual é o que possui a correlação não-linear mais forte com a violência. Se um gestor público tivesse recursos limitados, a IA sugere que investir neste pilar traria a maior variação na taxa de homicídios.")

# ==========================================
# ABA 2: MATRIZ DE CORRELAÇÃO DE PEARSON
# ==========================================
with tab_corr:
    st.markdown("### Mapa de Calor: Relações Matemáticas")
    st.caption("Veja como cada indicador interage com os outros. Cores frias (azul) indicam que quando um sobe o outro desce. Cores quentes (vermelho) indicam que ambos sobem juntos.")

    # Calcula a matriz de correlação cruzando Homicídios, o IGMA Geral e os 6 Pilares
    colunas_corr = ['Taxa_Homicidios_100k', 'IGMA'] + pilares
    matriz_corr = df_ml[colunas_corr].corr()

    # Simplificando os nomes para o gráfico não ficar gigante
    nomes_curtos = ['Homicídios', 'IGMA Geral', 'Governança', 'Educação', 'Saúde', 'Infraestrutura', 'Sustentabilidade', 'Desenv. Socioeconômico']
    matriz_corr.columns = nomes_curtos
    matriz_corr.index = nomes_curtos

    # Gráfico de Heatmap
    fig_heatmap = px.imshow(
        matriz_corr,
        text_auto=".2f",
        aspect="auto",
        color_continuous_scale="RdBu_r", # Vermelho para positivo, Azul para negativo
        zmin=-1, zmax=1
    )
    
    fig_heatmap.update_layout(height=600, margin=dict(t=20, b=20))
    st.plotly_chart(fig_heatmap, use_container_width=True, theme="streamlit")
