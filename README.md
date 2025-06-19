# Painel de Inspeções - Vigilância Sanitária de Ipojuca

Este é um painel interativo desenvolvido em Python usando Streamlit, que permite acompanhar as inspeções realizadas pela Vigilância Sanitária de Ipojuca. Os dados são alimentados manualmente por uma planilha Excel hospedada no OneDrive.

## 🚀 Funcionalidades
- Filtros por Protocolo, Estabelecimento, CNPJ, Atividade, Classificação, Território, Situação e Entrada (período).
- Resumo dos dados quando selecionado um único protocolo.
- Indicadores de desempenho para:
  - Inspeções no prazo
  - Licenciamentos no prazo
- Gráficos de distribuição por Território e Classificação.
- Visualização de dados filtrados em tabela.

## 🗂️ Organização do Painel
- **Lado Esquerdo:** Filtros e Resumo da Seleção.
- **Lado Direito:** Indicadores, Gráficos e Tabela de Dados.

## 🔧 Instalação e Execução

### 1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/painel-vigilancia-sanitaria.git
cd painel-vigilancia-sanitaria
2. Crie um ambiente virtual (opcional, mas recomendado):
bash
Copiar
Editar
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows
3. Instale as dependências:
bash
Copiar
Editar
pip install -r requirements.txt
4. Execute o painel:
bash
Copiar
Editar
streamlit run painel_vigilancia_sanitaria.py
🌐 Hospedagem Online
O painel pode ser hospedado de forma gratuita no Streamlit Cloud:

Suba o projeto para um repositório no GitHub.

Acesse o site do Streamlit Cloud e conecte sua conta do GitHub.

Escolha o repositório e o arquivo painel_vigilancia_sanitaria.py para rodar.

Configure os secrets se necessário.

🔗 Fonte dos Dados
Os dados são carregados automaticamente da seguinte planilha Excel hospedada no OneDrive:
Link para a planilha

👨‍💻 Desenvolvido por
Setor de Vigilância Sanitária - Ipojuca

yaml
Copiar
Editar

---

Se desejar, posso gerar também os arquivos ZIP prontos para você subir no GitHub. 