import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import unidecode

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

@st.cache_data
def carregar_dados():
    url = 'https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv'
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.upper()
    df.columns = df.columns.map(lambda x: unidecode.unidecode(x))
    return df

df = carregar_dados()

# Mapear colunas da planilha para nomes usados no código
# Colunas origem (coluna e nome original)
# A - PROTOCOLO
# B - CNPJ
# C - ESTABELECIMENTO (ou NOME)
# E - ATIVIDADE e CLASSIFICACAO (confirmar se são mesmo a mesma coluna ou diferentes)
# H - TERRITORIO
# F - ENTRADA
# M - CONCLUSÃO (usada como SITUAÇÃO)
# N - DATA CONCLUSÃO (usada como CONCLUSÃO)
# O - PREVISAO CONCLUSAO
# J - 1ª INSPECAO
# P - JUSTIFICATIVA

# Garantir que as colunas que usaremos existam e estejam mapeadas para o nome correto no código
colunas_esperadas = {
    'PROTOCOLO': 0,
    'CNPJ': 1,
    'ESTABELECIMENTO': 2,
    'ATIVIDADE': 4,
    'CLASSIFICACAO': 4,  # Mesmo índice da atividade (confirme se são a mesma coluna)
    'TERRITORIO': 7,
    'ENTRADA': 5,
    'SITUACAO': 12,      # Coluna M "CONCLUSÃO" na planilha, mas no código chama-se SITUACAO
    'CONCLUSAO': 13,     # Coluna N "DATA CONCLUSÃO" na planilha, mas no código chama-se CONCLUSAO
    'PREVISAO_CONCLUSAO': 14,
    '1A_INSPECAO': 9,
    'JUSTIFICATIVA': 15
}

# Criar as colunas no dataframe com os nomes que usaremos no código, copiando da planilha original conforme índice
for nome_col, idx in colunas_esperadas.items():
    if nome_col not in df.columns:
        if df.shape[1] > idx:
            df[nome_col] = df.iloc[:, idx]
        else:
            df[nome_col] = pd.NA

# Converter colunas de data
df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
df['1A_INSPECAO'] = pd.to_datetime(df['1A_INSPECAO'], errors='coerce')
df['CONCLUSAO'] = pd.to_datetime(df['CONCLUSAO'], errors='coerce')
df['PREVISAO_CONCLUSAO'] = pd.to_datetime(df['PREVISAO_CONCLUSAO'], errors='coerce')

# Filtros no sidebar
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', df['PROTOCOLO'].dropna().unique())
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', df['ESTABELECIMENTO'].dropna().unique())
filtro_cnpj = st.sidebar.multiselect('CNPJ', df['CNPJ'].dropna().unique())
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', df['ATIVIDADE'].dropna().unique())
filtro_classificacao = st.sidebar.multiselect('CLASSIFICACAO', df['CLASSIFICACAO'].dropna().unique())
filtro_territorio = st.sidebar.multiselect('TERRITORIO', df['TERRITORIO'].dropna().unique())
filtro_situacao = st.sidebar.multiselect('SITUACAO', df['SITUACAO'].dropna().unique())

data_hoje = datetime.today()
data_inicio, data_fim = st.sidebar.date_input('ENTRADA (Período)', [data_hoje, data_hoje])

# Aplicar filtros
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
    df_filtrado = df_filtrado[(df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) & (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))]

# Resumo da seleção
if len(filtro_protocolo) == 1:
    resumo = df_filtrado[df_filtrado['PROTOCOLO'] == filtro_protocolo[0]]
    if not resumo.empty:
        dados_resumo = resumo.iloc[0]
        st.sidebar.subheader('Resumo da Seleção')
        st.sidebar.markdown(f"""
        **Estabelecimento:** {dados_resumo.get('ESTABELECIMENTO', '')}
        **Protocolo:** {dados_resumo.get('PROTOCOLO', '')}
        **Atividade:** {dados_resumo.get('ATIVIDADE', '')}
        **Classificação:** {dados_resumo.get('CLASSIFICACAO', '')}
        **Território:** {dados_resumo.get('TERRITORIO', '')}
        **Situação:** {dados_resumo.get('SITUACAO', '')}
        **Justificativa:** {dados_resumo.get('JUSTIFICATIVA', '')}
        """)

# Indicadores de desempenho
st.subheader('Indicadores de Desempenho')

if filtro_classificacao and data_inicio and data_fim:
    for classificacao in filtro_classificacao:
        dados = df_filtrado[df_filtrado['CLASSIFICACAO'] == classificacao]

        if not dados.empty:
            total = len(dados)

            dentro_prazo_visita = dados.apply(lambda row:
                (pd.notnull(row['1A_INSPECAO']) and row['1A_INSPECAO'] <= row['ENTRADA'] + timedelta(days=30))
                or (pd.isnull(row['1A_INSPECAO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=30)),
                axis=1).sum()

            perc_visita = dentro_prazo_visita / total * 100 if total > 0 else 0

            dentro_prazo_conclusao = dados.apply(lambda row:
                (pd.notnull(row['CONCLUSAO']) and row['CONCLUSAO'] <= row['ENTRADA'] + timedelta(days=90))
                or (pd.isnull(row['CONCLUSAO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=90)),
                axis=1).sum()

            perc_conclusao = dentro_prazo_conclusao / total * 100 if total > 0 else 0

            st.markdown(f"""
            ### {classificacao}
            - **Inspecionados no Prazo:** {perc_visita:.2f}%
            - **Licenciados no Prazo:** {perc_conclusao:.2f}%
            """)

# Gráficos
g1 = px.bar(df_filtrado, x='TERRITORIO', color='CLASSIFICACAO', title='Inspeções por Território')
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(df_filtrado, x='CLASSIFICACAO', title='Distribuição por Classificação')
st.plotly_chart(g2, use_container_width=True)

# Tabela
st.subheader('Tabela de Dados Filtrados')
st.dataframe(df_filtrado)

st.caption('Vigilância Sanitária de Ipojuca - 2025')
