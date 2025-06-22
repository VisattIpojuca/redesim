# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este painel foi desenvolvido utilizando Streamlit para acompanhamento das inspeções da Vigilância Sanitária de Ipojuca. Ele permite:

- Filtros dinâmicos por protocolo, CNPJ, estabelecimento, atividade, classificação, território, situação e entrada.
- Cálculo de dois indicadores principais:
  - **1ª Visita em até 30 dias**
  - **Processo finalizado em até 90 dias**
- Visualização de gráficos dinâmicos e tabela interativa.
- Download do relatório Excel contendo:
  - Dados filtrados
  - Resumo dos indicadores
  - Justificativas dos processos Indeferidos

## Como executar

1. Clone o repositório.
2. Instale as dependências:
```bash
pip install -r requirements.txt
