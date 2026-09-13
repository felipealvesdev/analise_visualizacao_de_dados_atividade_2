# 📊 Dashboard Desenrola Brasil

Painel analítico interativo desenvolvido em **Streamlit** para explorar os dados
do programa **Desenrola Brasil**, com tratamento de outliers via IQR por banco.

## 🎯 Objetivo

Analisar o **volume financeiro** e o **número de operações** do programa Desenrola Brasil
por banco, UF e período, removendo outliers que distorcem a visualização dos dados.

## 🛠️ Tecnologias

- Python 3.14
- Streamlit 1.63
- Pandas 3.0
- Plotly 7.0
- NumPy 2.5

## 📁 Estrutura do projeto

```
.
├── .streamlit/
│   └── config.toml              # Tema customizado
├── assets/
│   └── dashboard-cover.png      # Banner estático
├── data/
│   └── dados_desenrola.csv      # Dataset
├── src/
│   ├── __init__.py
│   ├── data_loader.py           # Carregamento e pré-processamento
│   └── outliers.py              # Detecção de outliers via IQR
├── app.py                       # Ponto de entrada do dashboard
├── gerar_banner.py              # Script para gerar o banner (opcional)
├── requirements.txt
└── README.md
```

## 🚀 Como rodar

### 1. Clone ou baixe o projeto

```bash
git clone https://github.com/SEU-USUARIO/desenrola-dashboard.git
cd desenrola-dashboard
```

### 2. Crie e ative um ambiente virtual

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Rode o dashboard

```bash
streamlit run app.py
```

Acesse em `http://localhost:8501`.

## 📈 Funcionalidades

- **4 gráficos interativos** (Plotly Express):
  - Evolução mensal do volume por banco
  - Ranking de bancos por volume
  - Ticket médio × nº de operações
  - Box plot da distribuição de volume
- **5 widgets** na barra lateral: período, tipo de Desenrola, UF,
  toggle de remoção de outliers e sensibilidade do IQR.
- **Tratamento de outliers** via IQR **por banco** — evita penalizar
  grandes instituições que naturalmente operam volumes maiores.
- **Diagnóstico transparente**: exibe outliers removidos e métricas
  antes/depois da remoção.
- **Download** dos dados filtrados em CSV.

## 🔬 Metodologia de outliers

Foi utilizado o método **IQR (Intervalo Interquartílico)**, aplicado
**dentro de cada banco** para não remover operações legítimas de
instituições grandes como Bradesco, Itaú e Santander.

Limite inferior = Q1 − 1.5 × IQR  
Limite superior = Q3 + 1.5 × IQR

O usuário pode ajustar o multiplicador (de 1.0 a 3.0) na barra lateral.

## 💡 Principais insights

- **SP, RJ e MG** concentram a maior parte do volume, refletindo o peso
  econômico desses estados.
- **BTG Pactual** e **Votorantim** têm ticket médio alto com poucas
  operações (atendimento de alta renda).
- **Nubank** e **Inter** têm ticket médio baixo com alto volume
  (atendimento de varejo).
- Há um **salto visível no volume** a partir de maio/2025, quando começam
  a aparecer os registros com sufixo *PRUDENCIAL*, indicando nova fase
  do programa.

## 👨‍💻 Autor

Desenvolvido para a **Atividade II — Análise e Visualização de Dados**
| CESAR School.