# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este é um painel desenvolvido em Python com Streamlit para acompanhar as inspeções da Vigilância Sanitária do município de Ipojuca, alimentado automaticamente por uma planilha no Google Sheets.

## 🔗 Link da Planilha

A planilha de dados está disponível em:

[Planilha Google Sheets](https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/edit?gid=502962216)

## ⚙️ Funcionalidades

- Filtros laterais por:
  - Protocolo
  - CNPJ
  - Estabelecimento
  - Atividade
  - Classificação
  - Território
  - Situação
  - Período de Entrada (com seleção no formato calendário)
- Resumo detalhado da seleção (quando filtrado por um único protocolo).
- Indicadores de desempenho:
  - Percentual de inspeções realizadas no prazo.
  - Percentual de licenciamentos concluídos no prazo.
- Gráficos dinâmicos.
- Tabela detalhada dos dados filtrados.

## 📈 Regras dos Indicadores

- **Alto Risco:** Meta de 80% das inspeções e licenciamentos no prazo (30 dias para inspeção, 90 dias para conclusão).
- **Médio Risco:** Meta de 100% no prazo (30 dias para inspeção, 90 dias para conclusão).
- **Baixo Risco:** Meta de 50% das inspeções em até 30 dias.

## 🚀 Como Executar Localmente

### 1. Clone o projeto:

```bash
git clone https://github.com/seuusuario/seurepositorio.git
cd seurepositorio
