import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)

    df.rename(columns={
        'NOME': 'ESTABELECIMENTO',
        'CONCLUSÃO': 'SITUAÇÃO',
        'DATA CONCLUSÃO': 'DATA_CONCLUSAO',
        'PREV 1ª INSP': 'PREVISAO_1A_INSP'
    }, inplace=True)

    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
    df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], errors='coerce')
    df['DATA_CONCLUSAO'] = pd.to_datetime(df['DATA_CONCLUSAO'], errors='coerce')
    df['PREVISÃO CONCLUSÃO'] = pd.to_datetime(df['PREVISÃO CONCLUSÃO'], errors='coerce')
    df['PREVISAO_1A_INSP'] = pd.to_datetime(df['PREVISAO_1A_INSP'], errors='coerce')

    return df

df = carregar_dados()

# Filtros
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', sorted(df['PROTOCOLO'].dropna().unique()))
filtro_cnpj = st.sidebar.multiselect('CNPJ', sorted(df['CNPJ'].dropna().unique()))
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', sorted(df['ESTABELECIMENTO'].dropna().unique()))
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', sorted(df['ATIVIDADE'].dropna().unique()))
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', sorted(df['CLASSIFICAÇÃO'].dropna().unique()))
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', sorted(df['TERRITÓRIO'].dropna().unique()))
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', sorted(df['SITUAÇÃO'].dropna().unique()))

# Filtro de datas
data_min = df['ENTRADA'].min()
data_max = df['ENTRADA'].max()
data_inicio, data_fim = st.sidebar.date_input('PERÍODO', [data_min, data_max], min_value=data_min, max_value=data_max)

# Filtro do Indicador
indicador_selecionado = st.sidebar.selectbox(
    "Selecione o Indicador",
    ["", "1ª Visita em até 30 dias", "Processo finalizado em até 90 dias"]
)

# Aplicar filtros
df_filtrado = df.copy()
if filtro_protocolo:
    df_filtrado = df_filtrado[df_filtrado['PROTOCOLO'].isin(filtro_protocolo)]
if filtro_cnpj:
    df_filtrado = df_filtrado[df_filtrado['CNPJ'].isin(filtro_cnpj)]
if filtro_estab:
    df_filtrado = df_filtrado[df_filtrado['ESTABELECIMENTO'].isin(filtro_estab)]
if filtro_atividade:
    df_filtrado = df_filtrado[df_filtrado['ATIVIDADE'].isin(filtro_atividade)]
if filtro_classificacao:
    df_filtrado = df_filtrado[df_filtrado['CLASSIFICAÇÃO'].isin(filtro_classificacao)]
if filtro_territorio:
    df_filtrado = df_filtrado[df_filtrado['TERRITÓRIO'].isin(filtro_territorio)]
if filtro_situacao:
    df_filtrado = df_filtrado[df_filtrado['SITUAÇÃO'].isin(filtro_situacao)]

# Filtro de período
df_filtrado = df_filtrado[
    (df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
    (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))
]

# Cálculo dos Indicadores
if indicador_selecionado == "1ª Visita em até 30 dias":
    df_30 = df_filtrado.copy()

    df_30_validos = df_30[
        (df_30['SITUAÇÃO'].notna()) &
        (df_30['SITUAÇÃO'] != "AGUARDANDO 1ª INSPEÇÃO") &
        (df_30['1ª INSPEÇÃO'].notna()) &
        (df_30['PREVISAO_1A_INSP'].notna()) &
        (df_30['1ª INSPEÇÃO'] <= df_30['PREVISAO_1A_INSP'])
    ]

    numerador_30 = len(df_30_validos)
    denominador_30 = len(df_filtrado)
    percentual_30 = (numerador_30 / denominador_30 * 100) if denominador_30 > 0 else 0

    st.markdown(f"""
    ## 🕒 Indicador: 1ª Visita em até 30 dias
    - ✅ **{percentual_30:.2f}%** no prazo
    - 🎯 **Numerador:** {numerador_30}
    - 📊 **Denominador:** {denominador_30}
    """)

elif indicador_selecionado == "Processo finalizado em até 90 dias":
    df_90 = df_filtrado[
        ~df_filtrado['SITUAÇÃO'].isin(["EM INSPEÇÃO", "AGUARDANDO 1ª INSPEÇÃO", "PENDÊNCIA DOCUMENTAL"])
    ]

    filtro_valido_90 = (
        (df_90['DATA_CONCLUSAO'].notna()) &
        (df_90['DATA_CONCLUSAO'] <= df_90['PREVISÃO CONCLUSÃO'])
    )

    numerador_90 = filtro_valido_90.sum()
    denominador_90 = len(df_filtrado)
    percentual_90 = (numerador_90 / denominador_90 * 100) if denominador_90 > 0 else 0

    st.markdown(f"""
    ## 📜 Indicador: Processo finalizado em até 90 dias
    - ✅ **{percentual_90:.2f}%** no prazo
    - 🎯 **Numerador:** {numerador_90}
    - 📊 **Denominador:** {denominador_90}
    """)
