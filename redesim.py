import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

# Função para carregar dados da planilha do Google Sheets
@st.cache_data
def carregar_dados():
    url = 'https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv'
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()  # Padroniza nomes das colunas
    return df

# Carregar dados
df = carregar_dados()

# Checagem e criação da coluna PREVISÃO CONCLUSÃO (Coluna O = posição 14)
if 'PREVISÃO CONCLUSÃO' not in df.columns and df.shape[1] >= 15:
    df['PREVISÃO CONCLUSÃO'] = df.iloc[:, 14]

# Conversão de datas
df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], errors='coerce')
df['CONCLUSÃO'] = pd.to_datetime(df['CONCLUSÃO'], errors='coerce')
df['PREVISÃO CONCLUSÃO'] = pd.to_datetime(df['PREVISÃO CONCLUSÃO'], errors='coerce')

# ==================== 🔍 FILTROS ====================
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', df['PROTOCOLO'].dropna().unique())
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', df['ESTABELECIMENTO'].dropna().unique())
filtro_cnpj = st.sidebar.multiselect('CNPJ', df['CNPJ'].dropna().unique())
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', df['ATIVIDADE'].dropna().unique())
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', df['CLASSIFICAÇÃO'].dropna().unique())
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', df['TERRITÓRIO'].dropna().unique())
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', df['SITUAÇÃO'].dropna().unique())

# Filtro de datas com seleção tipo calendário
data_hoje = datetime.today()
data_inicio, data_fim = st.sidebar.date_input(
    'ENTRADA (Período)',
    [data_hoje, data_hoje]
)

# ==================== 🔧 APLICANDO FILTROS ====================
df_filtrado = df.copy()

if filtro_protocolo:
    df_filtrado = df_filtrado[df_filtrado['PROTOCOLO'].isin(filtro_protocolo)]
if filtro_estab:
    df_filtrado = df_filtrado[df_filtrado['ESTABELECIMENTO'].isin(filtro_estab)]
if filtro_cnpj:
    df_filtrado = df_filtrado[df_filtrado['CNPJ'].isin(filtro_cnpj)]
if filtro_atividade:
    df_filtrado = df_filtrado[df_filtrado['ATIVIDADE'].isin(filtro_atividade)]
if filtro_classificacao:
    df_filtrado = df_filtrado[df_filtrado['CLASSIFICAÇÃO'].isin(filtro_classificacao)]
if filtro_territorio:
    df_filtrado = df_filtrado[df_filtrado['TERRITÓRIO'].isin(filtro_territorio)]
if filtro_situacao:
    df_filtrado = df_filtrado[df_filtrado['SITUAÇÃO'].isin(filtro_situacao)]
if data_inicio and data_fim:
    df_filtrado = df_filtrado[
        (df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
        (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))
    ]

# ==================== 📋 RESUMO DA SELEÇÃO ====================
if len(filtro_protocolo) == 1:
    resumo = df_filtrado[df_filtrado['PROTOCOLO'] == filtro_protocolo[0]]

    if not resumo.empty:
        dados_resumo = resumo.iloc[0]
        st.sidebar.subheader('Resumo da Seleção')
        st.sidebar.markdown(f"""
        **Estabelecimento:** {dados_resumo.get('ESTABELECIMENTO', '')}
        **Protocolo:** {dados_resumo.get('PROTOCOLO', '')}
        **Atividade:** {dados_resumo.get('ATIVIDADE', '')}
        **Classificação:** {dados_resumo.get('CLASSIFICAÇÃO', '')}
        **Território:** {dados_resumo.get('TERRITÓRIO', '')}
        **Situação:** {dados_resumo.get('SITUAÇÃO', '')}
        **Justificativa:** {dados_resumo.get('JUSTIFICATIVA', '')}
        """)

# ==================== 📊 INDICADORES ====================
st.subheader('Indicadores de Desempenho')

if filtro_classificacao and data_inicio and data_fim:
    for classificacao in filtro_classificacao:
        dados = df_filtrado[df_filtrado['CLASSIFICAÇÃO'] == classificacao]

        if not dados.empty:
            total = len(dados)

            # 🎯 Inspecionados no prazo (30 dias)
            dentro_prazo_visita = dados.apply(
                lambda row: (
                    pd.notnull(row['1ª INSPEÇÃO']) and 
                    (row['1ª INSPEÇÃO'] <= row['ENTRADA'] + timedelta(days=30))
                ) or (
                    pd.isnull(row['1ª INSPEÇÃO']) and 
                    (datetime.now() <= row['ENTRADA'] + timedelta(days=30))
                ),
                axis=1
            ).sum()

            perc_visita = dentro_prazo_visita / total * 100 if total > 0 else 0

            # 🎯 Licenciados no prazo (90 dias)
            dentro_prazo_conclusao = dados.apply(
                lambda row: (
                    pd.notnull(row['CONCLUSÃO']) and 
                    (row['CONCLUSÃO'] <= row['ENTRADA'] + timedelta(days=90))
                ) or (
                    pd.isnull(row['CONCLUSÃO']) and 
                    (datetime.now() <= row['ENTRADA'] + timedelta(days=90))
                ),
                axis=1
            ).sum()

            perc_conclusao = dentro_prazo_conclusao / total * 100 if total > 0 else 0

            # 🔥 Mostrando no painel
            st.markdown(f"""
            ### {classificacao}
            - **Inspecionados no Prazo:** {perc_visita:.2f}%
            - **Licenciados no Prazo:** {perc_conclusao:.2f}%
            """)

# ==================== 📈 GRÁFICOS ====================
g1 = px.bar(
    df_filtrado, 
    x='TERRITÓRIO', 
    color='CLASSIFICAÇÃO', 
    title='Inspeções por Território'
)
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(
    df_filtrado, 
    x='CLASSIFICAÇÃO', 
    title='Distribuição por Classificação'
)
st.plotly_chart(g2, use_container_width=True)

# ==================== 🗂️ TABELA ====================
st.subheader('Tabela de Dados Filtrados')
st.dataframe(df_filtrado)

st.caption('Vigilância Sanitária de Ipojuca - 2025')
