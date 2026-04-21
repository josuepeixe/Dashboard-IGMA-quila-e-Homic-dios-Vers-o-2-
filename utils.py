import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

@st.cache_data(ttl=600)
def load_data():
    # Conexão com Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)
    df = conn.read()
    
    # Tratamento de colunas numéricas
    pilares = [
        'Governança, Eficiência Fiscal e Transparência', 'Educação', 
        'Saúde e Bem-Estar', 'Infraestrutura e Mobilidade Urbana', 
        'Sustentabilidade', 'Desenvolvimento Socioeconômico e Ordem Pública'
    ]
    cols_num = ['IGMA', 'Taxa_Homicidios_100k', 'Populacao'] + pilares
    for col in cols_num:
        if col in df.columns:
            if df[col].dtype == object:
                df[col] = df[col].str.replace(',', '.')
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Coluna auxiliar para filtros e exibição
    df['Cidade_Exibicao'] = df['Cidade'] + ' - ' + df['UF']
    return df

def aplicar_estilo_comum():
    st.markdown("""
    <style>
        /* Estilização da Barra Lateral de Navegação */
        [data-testid="stSidebarNav"] {
            padding-top: 2rem;
        }
        [data-testid="stSidebarNav"] span {
            font-size: 1.1rem;
            font-weight: 500;
            letter-spacing: 0.5px;
        }
        /* Cor de fundo sutil para o item selecionado */
        [data-testid="stSidebarNavLink"] {
            border-radius: 8px;
            margin: 0 10px;
            transition: all 0.3s ease;
        }
        [data-testid="stSidebarNavLink"]:hover {
            background-color: rgba(59, 130, 246, 0.1);
        }
        .block-container { padding-top: 2rem; }
        .gradient-text {
            background: -webkit-linear-gradient(45deg, #3B82F6, #10B981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800; font-size: 2.5rem;
        }
        .card {
            background: #1E293B; border: 1px solid #334155;
            padding: 20px; border-radius: 15px; text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .kpi-title { color: #94A3B8; font-size: 0.8rem; text-transform: uppercase; }
        .kpi-value { color: white; font-size: 1.8rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)
