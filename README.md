# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este é um painel desenvolvido para a Vigilância Sanitária de Ipojuca, com o objetivo de monitorar os processos de inspeção e licenciamento sanitário no município.

Os dados são atualizados automaticamente a partir de uma planilha no Google Sheets, alimentada manualmente pelo setor.

## 🚀 Funcionalidades

- Filtros por:
  - Protocolo
  - CNPJ
  - Estabelecimento
  - Atividade
  - Classificação de Risco
  - Território
  - Situação
  - Período de Entrada (com calendário)

- Resumo detalhado da seleção quando filtrado por um único protocolo.

- Indicadores de desempenho:
  - **Inspecionados no Prazo:** Percentual de inspeções realizadas em até 30 dias após a entrada do processo.
  - **Licenciados no Prazo:** Percentual de licenças sanitárias concluídas em até 90 dias após a entrada (exceto processos indeferidos).

- Metas:
  - **Alto Risco:** ≥ 80% (inspeção e licenciamento no prazo).
  - **Médio Risco:** ≥ 100% (inspeção e licenciamento no prazo).
  - **Baixo Risco:** ≥ 50% (apenas para inspeções no prazo).

- Gráficos dinâmicos:
  - Distribuição por Território.
  - Distribuição por Classificação.

- **Download do relatório em Excel**, com:
  - Aba de dados filtrados.
  - Aba de resumo dos indicadores.
  - Aba explicando como são feitos os cálculos.

## 🔗 Fonte dos Dados

- Dados alimentados manualmente pela equipe da Vigilância Sanitária.
- Planilha do Google Sheets:  
[🔗 Link para a Planilha](https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/edit)

## 🛠️ Instalação e Execução Local

1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
