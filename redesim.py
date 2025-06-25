import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)

    df.rename(columns={
        'NOME': 'ESTABELECIMENTO',
        'CONCLUSÃO': 'SITUAÇÃO',
        'DATA CONCLUSÃO': 'DATA_CONCLUSAO'
    }, inplace=True)

    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
    df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], errors='coerce')
    df['DATA_CONCLUSAO'] = pd.to_datetime(df['DATA_CONCLUSAO'], errors='coerce')
    df['PREVISÃO CONCLUSÃO'] = pd.to_datetime(df['PREVISÃO CONCLUSÃO'], errors='coerce')
    df['PREVISAO_1A_INSP'] = pd.to_datetime(df['PREV 1ª INSP'], errors='coerce')

    return df

df = carregar_dados()

st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', sorted(df['PROTOCOLO'].dropna().unique()))
filtro_cnpj = st.sidebar.multiselect('CNPJ', sorted(df['CNPJ'].dropna().unique()))
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', sorted(df['ESTABELECIMENTO'].dropna().unique()))
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', sorted(df['ATIVIDADE'].dropna().unique()))
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', sorted(df['CLASSIFICAÇÃO'].dropna().unique()))
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', sorted(df['TERRITÓRIO'].dropna().unique()))
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', sorted(df['SITUAÇÃO'].dropna().unique()))

data_min = df['ENTRADA'].min()
data_max = df['ENTRADA'].max()
data_inicio, data_fim = st.sidebar.date_input('PERÍODO', [data_min, data_max], min_value=data_min, max_value=data_max)

# 🔽 Filtro de indicador — movido para o final e sem valor padrão
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

df_filtrado = df_filtrado[
    (df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
    (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))
]

# Resumo da seleção
if len(filtro_protocolo) == 1:
    resumo = df_filtrado[df_filtrado['PROTOCOLO'] == filtro_protocolo[0]]
    if not resumo.empty:
        r = resumo.iloc[0]
        st.sidebar.subheader('Resumo da Seleção')
        st.sidebar.markdown(f"""
        **Estabelecimento:** {r.get('ESTABELECIMENTO', '')}  
        **Protocolo:** {r.get('PROTOCOLO', '')}  
        **Atividade:** {r.get('ATIVIDADE', '')}  
        **Classificação:** {r.get('CLASSIFICAÇÃO', '')}  
        **Território:** {r.get('TERRITÓRIO', '')}  
        **Situação:** {r.get('SITUAÇÃO', '')}  
        **Justificativa:** {r.get('JUSTIFICATIVA', '')}  
        """)

# Indicadores — apenas se selecionado
if indicador_selecionado == "1ª Visita em até 30 dias":
    df_30 = df_filtrado.copy()
    df_30 = df_30[
        ~(
            (df_30['SITUAÇÃO'] == "AGUARDANDO 1ª INSPEÇÃO") |
            ((df_30['SITUAÇÃO'] == "INDEFERIDO") & (df_30['1ª INSPEÇÃO'].isna()))
        )
    ]
    filtro_valido_30 = (
        (pd.notnull(df_30['1ª INSPEÇÃO'])) &
        (df_30['1ª INSPEÇÃO'] <= df_30['PREVISAO_1A_INSP'])
    )
    numerador_30 = filtro_valido_30.sum()
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
        (pd.notnull(df_90['DATA_CONCLUSAO'])) &
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

# Gráfico de justificativas
st.subheader('Justificativas dos Indeferidos')
df_indeferido = df_filtrado[df_filtrado['SITUAÇÃO'] == "INDEFERIDO"]
if not df_indeferido.empty:
    graf_just = px.bar(
        df_indeferido.groupby('JUSTIFICATIVA').size().reset_index(name='Quantidade'),
        x='JUSTIFICATIVA',
        y='Quantidade',
        title='Distribuição das Justificativas (Indeferidos)',
        text_auto=True
    )
    st.plotly_chart(graf_just, use_container_width=True)
else:
    st.info("Não há registros com situação 'INDEFERIDO' no filtro atual.")

# Gráficos gerais
g1 = px.bar(df_filtrado, x='TERRITÓRIO', color='CLASSIFICAÇÃO', title='Distribuição de Inspeções por Território')
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(df_filtrado, x='CLASSIFICAÇÃO', title='Distribuição por Classificação')
st.plotly_chart(g2, use_container_width=True)

# Tabela com datas formatadas
st.subheader('Tabela de Dados Filtrados')
df_mostrar = df_filtrado.copy()
for col in df_mostrar.select_dtypes(include='datetime'):
    df_mostrar[col] = df_mostrar[col].dt.strftime('%d/%m/%Y')
st.dataframe(df_mostrar)

# Download Excel
st.subheader("📥 Baixar Relatório Excel")
buffer = io.BytesIO()
with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, sheet_name="Dados Filtrados", index=False)
    df_indeferido.to_excel(writer, sheet_name="Indeferidos", index=False)
    resumo = pd.DataFrame({
        'Indicador': ['1ª Visita em até 30 dias', 'Processo finalizado em até 90 dias'],
        'Numerador': [numerador_30 if 'numerador_30' in locals() else '',
                      numerador_90 if 'numerador_90' in locals() else ''],
        'Denominador': [denominador_30 if 'denominador_30' in locals() else '',
                        denominador_90 if 'denominador_90' in locals() else ''],
        'Percentual (%)': [percentual_30 if 'percentual_30' in locals() else '',
                           percentual_90 if 'percentual_90' in locals() else '']
    })
    resumo.to_excel(writer, sheet_name="Resumo dos Indicadores", index=False)

st.download_button(
    label="📄 Baixar Relatório Excel",
    data=buffer.getvalue(),
    file_name="Relatorio_VISA_Ipojuca.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption("Vigilância Sanitária de Ipojuca – 2025")
