# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este é um painel desenvolvido para a Vigilância Sanitária de Ipojuca, com o objetivo de monitorar os processos de inspeções, emissão de licenças e acompanhamento dos prazos.

## 🚀 Funcionalidades

- Filtros dinâmicos por:
  - Protocolo
  - CNPJ
  - Estabelecimento
  - Atividade
  - Classificação
  - Território
  - Situação
  - Entrada (com seletor de datas)

- Resumo da seleção quando selecionado um único protocolo.

- Cálculo de dois indicadores principais:
  - **1ª Visita em até 30 dias**  
    (Avalia se a primeira inspeção foi realizada até a data prevista — Coluna "PREV 1ª INSP".)

  - **Processo finalizado em até 90 dias**  
    (Avalia se o processo foi concluído até a data prevista — Coluna "PREVISÃO CONCLUSÃO".)

- Gráfico das justificativas dos processos **indeferidos**.

- Visualização de gráficos interativos:
  - Distribuição por território
  - Distribuição por classificação

- Tabela de dados filtrados.

- Exportação de relatório Excel com três abas:
  - Dados Filtrados
  - Resumo dos Indicadores
  - Justificativas dos Indeferidos

---

## 🛠️ Como Executar

1. Clone este repositório.

2. Instale as dependências com:

```bash
pip install -r requirements.txt
