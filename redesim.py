import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

# Função para carregar dados
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()

    # Renomear colunas manualmente
    df = df.rename(columns={
        'PROTOCOLO': 'PROTOCOLO',
        'CNPJ': 'CNPJ',
        'NOME': 'ESTABELECIMENTO',
        'ATIVIDADE': 'ATIVIDADE',
        'CLASSIFICACAO': 'CLASSIFICACAO',
        'TERRITORIO': 'TERRITORIO',
        'ENTRADA': 'ENTRADA',
        '1A INSPECAO': 'INSPECAO',
        'CONCLUSAO': 'SITUACAO',  # Coluna M
        'DATA CONCLUSAO': 'CONCLUSAO',  # Coluna N
        'PREVISAO CONCLUSAO': 'PREVISAO_CONCLUSAO',  # Coluna O
        'JUSTIFICATIVA': 'JUSTIFICATIVA'  # Coluna P
    })

    # Converter datas
    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
    df['INSPECAO'] = pd.to_datetime(df['INSPECAO'], errors='coerce')
    df['CONCLUSAO'] = pd.to_datetime(df['CONCLUSAO'], errors='coerce')
    df['PREVISAO_CONCLUSAO'] = pd.to_datetime(df['PREVISAO_CONCLUSAO'], errors='coerce')

    return df

df = carregar_dados()

# Filtros
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', df['PROTOCOLO'].dropna().unique())
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', df['ESTABELECIMENTO'].dropna().unique())
filtro_cnpj = st.sidebar.multiselect('CNPJ', df['CNPJ'].dropna().unique())
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', df['ATIVIDADE'].dropna().unique())
filtro_classificacao = st.sidebar.multiselect('CLASSIFICACAO', df['CLASSIFICACAO'].dropna().unique())
filtro_territorio = st.sidebar.multiselect('TERRITORIO', df['TERRITORIO'].dropna().unique())
filtro_situacao = st.sidebar.multiselect('SITUACAO', df['SITUACAO'].dropna().unique())

# Filtro de data com calendário
data_hoje = datetime.today()
data_inicio, data_fim = st.sidebar.date_input(
    'ENTRADA (Período)', [data_hoje, data_hoje])

# Aplicando os filtros
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

# Resumo da Seleção
if len(filtro_protocolo) == 1:
    resumo = df_filtrado[df_filtrado['PROTOCOLO'] == filtro_protocolo[0]]
    if not resumo.empty:
        dados = resumo.iloc[0]
        st.sidebar.subheader('Resumo da Seleção')
        st.sidebar.markdown(f"""
        **Estabelecimento:** {dados.get('ESTABELECIMENTO', '')}
        **Protocolo:** {dados.get('PROTOCOLO', '')}
        **Atividade:** {dados.get('ATIVIDADE', '')}
        **Classificação:** {dados.get('CLASSIFICACAO', '')}
        **Território:** {dados.get('TERRITORIO', '')}
        **Situação:** {dados.get('SITUACAO', '')}
        **Justificativa:** {dados.get('JUSTIFICATIVA', '')}
        """)

# Cálculo dos Indicadores
st.subheader('Indicadores de Desempenho')

if filtro_classificacao and data_inicio and data_fim:
    for classificacao in filtro_classificacao:
        dados = df_filtrado[df_filtrado['CLASSIFICACAO'] == classificacao]
        dados = dados[~dados['SITUACAO'].isin(['INDEFERIDO', None, ''])]

        total = len(dados)

        # Inspeção no prazo
        dentro_prazo_visita = dados.apply(lambda row:
            (pd.notnull(row['INSPECAO']) and row['INSPECAO'] <= row['ENTRADA'] + timedelta(days=30))
            or (pd.isnull(row['INSPECAO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=30)),
            axis=1).sum()

        perc_visita = (dentro_prazo_visita / total * 100) if total > 0 else 0

        # Conclusão no prazo
        dentro_prazo_conclusao = dados.apply(lambda row:
            (pd.notnull(row['CONCLUSAO']) and row['CONCLUSAO'] <= row['ENTRADA'] + timedelta(days=90))
            or (pd.isnull(row['CONCLUSAO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=90)),
            axis=1).sum()

        perc_conclusao = (dentro_prazo_conclusao / total * 100) if total > 0 else 0

        st.markdown(f"""
        ### {classificacao}
        - **Inspecionados no Prazo:** {perc_visita:.2f}%
        - **Licenciados no Prazo:** {perc_conclusao:.2f}%
        """)

# Gráficos
st.subheader('Visualização dos Dados')

g1 = px.bar(df_filtrado, x='TERRITORIO', color='CLASSIFICACAO', title='Inspeções por Território')
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(df_filtrado, x='CLASSIFICACAO', title='Distribuição por Classificação')
st.plotly_chart(g2, use_container_width=True)

# Tabela
st.subheader('Tabela de Dados Filtrados')
st.dataframe(df_filtrado)

st.caption('Vigilância Sanitária de Ipojuca - 2025')
