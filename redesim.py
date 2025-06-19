import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import io

st.set_page_config(page_title="Painel VISA Ipojuca", layout="wide")
st.title("Painel de Inspeções - Vigilância Sanitária de Ipojuca")

# 🔗 Função para carregar dados da planilha Google
@st.cache_data
def carregar_dados():
    url = "https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/export?format=csv"
    df = pd.read_csv(url)

    # Renomear colunas
    df.rename(columns={
        'NOME': 'ESTABELECIMENTO',
        'CONCLUSÃO': 'SITUAÇÃO',
        'DATA CONCLUSÃO': 'DATA_CONCLUSAO'
    }, inplace=True)

    # Conversão de datas
    df['ENTRADA'] = pd.to_datetime(df['ENTRADA'], errors='coerce')
    df['1ª INSPEÇÃO'] = pd.to_datetime(df['1ª INSPEÇÃO'], errors='coerce')
    df['DATA_CONCLUSAO'] = pd.to_datetime(df['DATA_CONCLUSAO'], errors='coerce')
    df['PREVISÃO CONCLUSÃO'] = pd.to_datetime(df['PREVISÃO CONCLUSÃO'], errors='coerce')

    return df

df = carregar_dados()

# 🔍 Filtros
st.sidebar.header('Filtros')

filtro_protocolo = st.sidebar.multiselect('PROTOCOLO', df['PROTOCOLO'].dropna().unique())
filtro_cnpj = st.sidebar.multiselect('CNPJ', df['CNPJ'].dropna().unique())
filtro_estab = st.sidebar.multiselect('ESTABELECIMENTO', df['ESTABELECIMENTO'].dropna().unique())
filtro_atividade = st.sidebar.multiselect('ATIVIDADE', df['ATIVIDADE'].dropna().unique())
filtro_classificacao = st.sidebar.multiselect('CLASSIFICAÇÃO', df['CLASSIFICAÇÃO'].dropna().unique())
filtro_territorio = st.sidebar.multiselect('TERRITÓRIO', df['TERRITÓRIO'].dropna().unique())
filtro_situacao = st.sidebar.multiselect('SITUAÇÃO', df['SITUAÇÃO'].dropna().unique())

# Filtro de data
data_hoje = datetime.today()
data_inicio, data_fim = st.sidebar.date_input('Período de ENTRADA', [data_hoje, data_hoje])

# Aplicação dos filtros
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
if data_inicio and data_fim:
    df_filtrado = df_filtrado[
        (df_filtrado['ENTRADA'] >= pd.to_datetime(data_inicio)) &
        (df_filtrado['ENTRADA'] <= pd.to_datetime(data_fim))
    ]

# 🔸 Resumo da seleção
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

# 🔸 Indicadores
st.subheader('Indicadores de Desempenho')

resumo_indicadores = []

if filtro_classificacao and data_inicio and data_fim:
    for classificacao in filtro_classificacao:
        dados = df_filtrado[df_filtrado['CLASSIFICAÇÃO'] == classificacao]
        dados = dados.copy()

        if classificacao in ['ALTO RISCO', 'MÉDIO RISCO']:
            meta_visita = 100 if classificacao == 'MÉDIO RISCO' else 80
            meta_licenca = meta_visita
        elif classificacao == 'BAIXO RISCO':
            meta_visita = 50
            meta_licenca = None

        total = len(dados)

        if total > 0:
            dentro_prazo_visita = dados.apply(
                lambda row: (pd.notnull(row['1ª INSPEÇÃO']) and row['1ª INSPEÇÃO'] <= row['ENTRADA'] + timedelta(days=30)) or
                            (pd.isnull(row['1ª INSPEÇÃO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=30)),
                axis=1
            ).sum()

            perc_visita = dentro_prazo_visita / total * 100

            dados_concluidos = dados[~dados['SITUAÇÃO'].isin([None, '', 'INDEFERIDO'])]
            total_concluidos = len(dados_concluidos)

            if classificacao != 'BAIXO RISCO':
                dentro_prazo_conclusao = dados_concluidos.apply(
                    lambda row: (pd.notnull(row['DATA_CONCLUSAO']) and row['DATA_CONCLUSAO'] <= row['ENTRADA'] + timedelta(days=90)) or
                                (pd.isnull(row['DATA_CONCLUSAO']) and datetime.now() <= row['ENTRADA'] + timedelta(days=90)),
                    axis=1
                ).sum()

                perc_conclusao = dentro_prazo_conclusao / total_concluidos * 100 if total_concluidos > 0 else 0

                st.markdown(f"""
                ### {classificacao}
                - **Inspecionados no Prazo:** {perc_visita:.2f}% (Meta ≥ {meta_visita}%)
                - **Licenciados no Prazo:** {perc_conclusao:.2f}% (Meta ≥ {meta_licenca}%)
                """)

                resumo_indicadores.append({
                    'Classificação': classificacao,
                    'Meta Inspeção (%)': meta_visita,
                    'Resultado Inspeção (%)': f'{perc_visita:.2f}',
                    'Meta Licença (%)': meta_licenca,
                    'Resultado Licença (%)': f'{perc_conclusao:.2f}'
                })

            else:
                st.markdown(f"""
                ### {classificacao}
                - **Inspecionados no Prazo:** {perc_visita:.2f}% (Meta ≥ {meta_visita}%)
                """)

                resumo_indicadores.append({
                    'Classificação': classificacao,
                    'Meta Inspeção (%)': meta_visita,
                    'Resultado Inspeção (%)': f'{perc_visita:.2f}',
                    'Meta Licença (%)': '',
                    'Resultado Licença (%)': ''
                })

# 🔸 Gráficos
g1 = px.bar(df_filtrado, x='TERRITÓRIO', color='CLASSIFICAÇÃO', title='Distribuição de Inspeções por Território')
st.plotly_chart(g1, use_container_width=True)

g2 = px.histogram(df_filtrado, x='CLASSIFICAÇÃO', title='Distribuição por Classificação')
st.plotly_chart(g2, use_container_width=True)

# 🔸 Tabela de Dados
st.subheader('Tabela de Dados Filtrados')
st.dataframe(df_filtrado)

# 🔥 Download do Relatório Excel
st.subheader('📥 Download do Relatório Excel')

output = io.BytesIO()

with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
    df_filtrado.to_excel(writer, sheet_name='Dados Filtrados', index=False)

    if resumo_indicadores:
        df_resumo = pd.DataFrame(resumo_indicadores)
        df_resumo.to_excel(writer, sheet_name='Resumo dos Indicadores', index=False)

        df_explicacao = pd.DataFrame({
            'Descrição': [
                'Inspecionados no Prazo: Nº de inspeções realizadas até 30 dias após ENTRADA ÷ Total de processos',
                'Licenciados no Prazo: Nº de licenças concluídas até 90 dias após ENTRADA ÷ Total de processos válidos (exceto indeferidos)',
                'Metas: Alto Risco ≥ 80%, Médio Risco ≥ 100%, Baixo Risco ≥ 50% (apenas para inspeções)'
            ]
        })
        df_explicacao.to_excel(writer, sheet_name='Como é Calculado', index=False)

# ✅ writer.save() foi removido! Não é necessário.

st.download_button(
    label="📥 Baixar Relatório Excel",
    data=output.getvalue(),
    file_name="Relatorio_VISA_Ipojuca.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

st.caption('Vigilância Sanitária de Ipojuca - 2025')
