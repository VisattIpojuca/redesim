import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

# Função para carregar os dados do Google Sheets
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)

    # Padronizar nomes das colunas
    df.columns = df.columns.str.strip().str.upper()

    # Renomear para uso interno
    df = df.rename(columns={
        'PROTOCOLO': 'PROTOCOLO',
        'CNPJ': 'CNPJ',
        'ESTABELECIMENTO': 'ESTABELECIMENTO',
        'ATIVIDADE': 'ATIVIDADE',
        'CLASSIFICAÇÃO': 'CLASSIFICACAO',
        'CLASSIFICACAO': 'CLASSIFICACAO',
        'TERRITÓRIO': 'TERRITORIO',
        'TERRITORIO': 'TERRITORIO',
        'ENTRADA': 'ENTRADA',
        '1ª INSPEÇÃO': 'INSPECAO',
        '1A INSPECAO': 'INSPECAO',
        'SITUAÇÃO': 'SITUACAO',
        'SITUACAO': 'SITUACAO',
        'DATA CONCLUSÃO': 'CONCLUSAO',
        'CONCLUSAO': 'CONCLUSAO',
        'PREVISAO CONCLUSAO': 'PREVISAO_CONCLUSAO',
        'PREVISÃO CONCLUSÃO': 'PREVISAO_CONCLUSAO',
        'JUSTIFICATIVA': 'JUSTIFICATIVA'
    })

    # Conversão de datas
    for coluna in ['ENTRADA', 'INSPECAO', 'CONCLUSAO', 'PREVISAO_CONCLUSAO']:
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce')

    return df


df = carregar_dados()

# ----- BARRA LATERAL - FILTROS -----
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', df['PROTOCOLO'].dropna().unique())
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', df['ESTABELECIMENTO'].dropna().unique())
filtro_cnpj = st.sidebar.multiselect('CNPJ', df['CNPJ'].dropna().unique())
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', df['ATIVIDADE'].dropna().unique())
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', df['CLASSIFICACAO'].dropna().unique())
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', df['TERRITORIO'].dropna().unique())
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', df['SITUACAO'].dropna().unique())

# Filtro de datas (ENTRADA)
data_hoje = datetime.today()
data_inicio, data_fim = st.sidebar.date_input('ENTRADA (Período)', [data_hoje, data_hoje])

# ----- APLICAR FILTROS -----
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
    df_filtrado = df_filtrado[df_filtrado['CLASSIFICACAO'].isin(filtro_classificacao)]
if filtro_territorio:
    df_filtrado = df_filtrado[df_filtrado['TERRITORIO'].isin(filtro_territorio)]
if filtro_situacao:
    df_filtrado = df_filtrado[df_filtrado['SITUACAO'].isin(filtro_situacao)]
if data_inicio and data_fim:
    df_filtrado = df_filtrado[(df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
                               (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))]

# ----- RESUMO DA SELEÇÃO -----
if len(filtro_protocolo) == 1:
    resumo = df_filtrado[df_filtrado['PROTOCOLO'] == filtro_protocolo[0]].iloc[0]
    st.sidebar.subheader('Resumo da Seleção')
    st.sidebar.markdown(f"""
    **Estabelecimento:** {resumo.get('ESTABELECIMENTO', '')}
    **Protocolo:** {resumo.get('PROTOCOLO', '')}
    **Atividade:** {resumo.get('ATIVIDADE', '')}
    **Classificação:** {resumo.get('CLASSIFICACAO', '')}
    **Território:** {resumo.get('TERRITORIO', '')}
    **Situação:** {resumo.get('SITUACAO', '')}
    **Justificativa:** {resumo.get('JUSTIFICATIVA', '')}
    """)

# ----- INDICADORES DE DESEMPENHO -----
st.subheader('Indicadores de Desempenho')

if filtro_classificacao and data_inicio and data_fim:
    for classificacao in filtro_classificacao:
        dados = df_filtrado[df_filtrado['CLASSIFICACAO'] == classificacao]

        if not dados.empty:
            total = len(dados)

            dentro_prazo_visita = dados.apply(lambda row: (
                (pd.notnull(row['INSPECAO']) and (row['INSPECAO'] <= row['ENTRADA'] + timedelta(days=30)))
                or (pd.isnull(row['INSPECAO']) and (datetime.now() <= row['ENTRADA'] + timedelta(days=30)))
            ), axis=1).sum()

            perc_visita = dentro_prazo_visita / total * 100 if total > 0 else 0

            # ---- Cálculo para Licenciados no Prazo ----
            dados_validos = dados[~dados['SITUACAO'].isin(['INDEFERIDO']) | dados['SITUACAO'].isna()]

            dentro_prazo_conclusao = dados_validos.apply(lambda row: (
                (pd.notnull(row['CONCLUSAO']) and (row['CONCLUSAO'] <= row['ENTRADA'] + timedelta(days=90)))
                or (pd.isnull(row['CONCLUSAO']) and (datetime.now() <= row['ENTRADA'] + timedelta(days=90)))
            ), axis=1).sum()

            total_conclusao = len(dados_validos)
            perc_conclusao = dentro_prazo_conclusao / total_conclusao * 100 if total_conclusao > 0 else 0

            st.markdown(f"""
            ### {classificacao}
            - **Inspecionados no Prazo:** {perc_visita:.2f}%
            - **Licenciados no Prazo:** {perc_conclusao:.2f}%
            """)

# ----- VISUALIZAÇÕES -----
g1 = px.bar(df_filtrado, x='TERRITORIO', color='CLASSIFICACAO', title='Inspeções por Território')
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(df_filtrado, x='CLASSIFICACAO', title='Distribuição por Classificação')
st.plotly_chart(g2, use_container_width=True)

st.subheader('Tabela de Dados Filtrados')
st.dataframe(df_filtrado)

st.caption('Vigilância Sanitária de Ipojuca - 2025')
