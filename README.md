📄 README.md— Painel VISA Ipojuca
redução de preço

Cópia

Editar
# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este painel interativo foi desenvolvido em **Python com Streamlit** para monitoramento das inspeções da Vigilância Sanitária de Ipojuca, utilizando dados alimentados manualmente por uma planilha do Google Sheets.

---

## 📊 Indicadores Monitorados

### 🕒 1ª Visita em até 30 dias

Calcula o percentual de processos que realizaram a **1ª inspeção dentro do prazo previsto**.

- **Numerador:** Entradas com **1ª INSPEÇÃO ≤ PREV 1ª INSPEÇÃO**, **exceto**:
  - Situações com `"AGUARDANDO 1ª INSPEÇÃO"`
  - Situações com `"INDEFERIDO"` e **1ª INSPEÇÃO em branco**

✅ Situações com `"PENDÊNCIA DOCUMENTAL"` **são consideradas**, se a inspeção foi realizada no prazo.

- **Denominador:** Todas as entradas (coluna `ENTRADA`)

---

### 📜 Processo finalizado em até 90 dias

Calcula o percentual de processos **concluídos dentro do prazo previsto para conclusão**.

- **Numerador:** Entradas com **DATA CONCLUSÃO ≤ PREVISÃO CONCLUSÃO**, **exceto**:
  - Situações com `"EM INSPEÇÃO"`, `"AGUARDANDO 1ª INSPEÇÃO"` ou `"PENDÊNCIA DOCUMENTAL"`

- **Denominador:** Todas as entradas (coluna `ENTRADA`)

---

## 📌 Funcionalidades

- Filtros interativos (Protocolo, CNPJ, Estabelecimento, Atividade, Classificação, Território, Situação e Período de Entrada)
- Resumo da seleção para protocolos individuais
- Gráficos por classificação, território e justificativas de indeferimento
- Indicadores dinâmicos com cálculo automatizado
- Exportação em Excel com 3 abas:
  - Dados Filtrados
  - Justificativas Indeferidos
  - Resumo dos Indicadores

---

## 🔗 Fonte dos Dados

A planilha usada está disponível em:
[Google Sheets - VISA Ipojuca](https://docs.google.com/spreadsheets/d/1nKoAEXQ0QZOrIt-0CMvW5MOt9Q_FC8Ak/edit?usp=sharing)

---

## ⚙️ Como Executar Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/painel-visa-ipojuca.git
cd painel-visa-ipojuca
2. Instalar as dependências
festança

Cópia

Editar
pip install -r requirements.txt
3. Execute o aplicativo
festança

Cópia

Editar
streamlit run painel_visa.py
🧪 Requisitos
Veja o arquivo requirements.txt, que inclui:

iluminado por fluxo

pandas

tramadamente

xlsxwriter

👨‍⚕️ Desenvolvido por
Vigilância Sanitária de Ipojuca
Secretaria Municipal de Saúde – 2025

📬 Dúvidas ou sugestões? Entre em contato com a equipe técnica.