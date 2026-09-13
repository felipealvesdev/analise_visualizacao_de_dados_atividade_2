# 📊 Dashboard Desenrola Brasil

<div align="center">

![Dashboard Cover](assets/dashboard-cover.png)

**Painel Analítico Interativo do Programa Desenrola Brasil**

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.63-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Plotly](https://img.shields.io/badge/Plotly-7.0-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)
[![Pandas](https://img.shields.io/badge/Pandas-3.0-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)

*Análise e Visualização de Dados · CESAR School*

</div>

---

## 👨‍💻 Autor

**Felipe Alexandre Alves da Silva**

Projeto desenvolvido para a disciplina **Análise e Visualização de Dados** — **Atividade II: Construção de um Dashboard com Streamlit** — **CESAR School**.

---

## 🎯 Sobre o Projeto

Este dashboard foi criado para **explorar visualmente** os dados do programa **Desenrola Brasil**, um programa do Governo Federal voltado à renegociação de dívidas. O painel permite analisar o **volume financeiro** e o **número de operações** por banco, Unidade Federativa (UF) e período, aplicando **tratamento estatístico de outliers** para garantir análises mais confiáveis.

O grande diferencial deste projeto é o **tratamento de outliers via IQR (Intervalo Interquartílico) aplicado dentro de cada banco**, que evita penalizar grandes instituições financeiras que naturalmente operam volumes muito maiores do que bancos menores.

---

## ✨ Funcionalidades

### 📈 Visualizações Interativas (Plotly Express)

| # | Gráfico | Descrição |
|---|---------|-----------|
| 1 | **Evolução Mensal do Volume** | Linha temporal mostrando o Top 8 bancos ao longo dos meses |
| 2 | **Ticket Médio × Nº de Operações** | Scatter plot relacionando porte da operação com volume total |
| 3 | **Box Plot de Distribuição** | Distribuição estatística do volume por banco |
| 4 | **Mapa Coroplético do Brasil** | Volume agregado por UF (com fallback para gráfico de barras offline) |
| 5 | **Comparador de Períodos** | Comparação A/B entre dois recortes de tempo |
| 6 | **Rankings em Cards** | Top 8 bancos por volume, por operações e Top 8 UFs |

### 🎛️ Widgets de Interação

- 🗓️ **Slider de Período** — seleção do intervalo de datas (MM/YYYY)
- 🏷️ **Pills Multi-seleção** — filtro por Tipo Desenrola (1, 2, 3)
- 🗺️ **Multiselect de UFs** — filtro por unidades federativas
- ⚙️ **Toggle de Outliers** — ativa/desativa remoção de outliers
- 🎚️ **Slider de Sensibilidade IQR** — ajusta o multiplicador (1.0 a 3.0)
- 📅 **Date Inputs A/B** — comparador de períodos
- 🧭 **Segmented Control** — navegação entre abas
- 🔄 **Botão de Reset** — limpa todos os filtros

### 🎨 Experiência do Usuário

- ✅ Tema **claro e escuro** com detecção automática
- ✅ Formatação brasileira de números (`R$ 1.234,56`, `12,34%`)
- ✅ Cards de ranking com CSS customizado
- ✅ Topbar estilo *ticker* com KPIs em tempo real
- ✅ Avisos contextuais sobre o uso de outliers
- ✅ Download dos dados filtrados em CSV

---

## 🛠️ Tecnologias Utilizadas

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| **Python** | 3.14 | Linguagem base |
| **Streamlit** | 1.63 | Framework do dashboard |
| **Plotly Express** | 7.0 | Visualizações interativas |
| **Pandas** | 3.0 | Manipulação de dados |
| **NumPy** | 2.5 | Cálculos numéricos |
| **Pillow** | 12.3 | Manipulação da imagem de capa |
| **Matplotlib** | 3.11 | Geração do banner (script opcional) |

---

## 📁 Estrutura do Projeto

```
desenrola-dashboard/
│
├── .streamlit/
│   └── config.toml                  # Tema customizado (cores, layout)
│
├── assets/
│   └── dashboard-cover.png          # Banner/imagem de capa do dashboard
│
├── data/
│   └── dados_desenrola.csv          # Dataset do Desenrola Brasil
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py               # Carregamento e pré-processamento
│   └── outliers.py                  # Detecção de outliers via IQR
│
├── app.py                           # 🚀 Ponto de entrada do dashboard
├── gerar_banner.py                  # Script para regenerar o banner (opcional)
├── requirements.txt                 # Dependências do projeto
└── README.md                        # Este arquivo
```

---

## 🚀 Como Rodar o Projeto — Passo a Passo

### 📋 Pré-requisitos

Antes de começar, certifique-se de ter instalado em sua máquina:

- **Python 3.10 ou superior** ([download](https://www.python.org/downloads/))
- **pip** (gerenciador de pacotes, já vem com o Python)
- **Git** (opcional, apenas se quiser clonar o repositório)

Para verificar se o Python está instalado corretamente, abra o terminal e digite:

```bash
python --version
```

Você deve ver algo como `Python 3.14.x`.

---

### 🔽 Passo 1 — Obter o projeto

**Opção A — Clonar via Git:**

```bash
git clone https://github.com/SEU-USUARIO/desenrola-dashboard.git
cd desenrola-dashboard
```

**Opção B — Baixar o ZIP:**

1. Faça o download do arquivo `.zip` disponibilizado no Classroom
2. Descompacte em uma pasta de sua preferência
3. Abra o terminal dentro dessa pasta

---

### 🐍 Passo 2 — Criar um ambiente virtual (altamente recomendado)

O uso de ambiente virtual evita conflitos com outras bibliotecas já instaladas no sistema.

**Windows (PowerShell):**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

> ⚠️ Se aparecer erro de execução de scripts no PowerShell, execute primeiro:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

**Windows (Prompt de Comando - CMD):**

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Quando o ambiente estiver ativo, você verá `(.venv)` no início da linha do terminal. ✅

---

### 📦 Passo 3 — Instalar as dependências

Com o ambiente virtual ativado, execute:

```bash
pip install -r requirements.txt
```

Isso instalará **todas** as bibliotecas necessárias (Streamlit, Plotly, Pandas, NumPy, etc.). O processo pode levar de 1 a 3 minutos.

Se quiser atualizar o `pip` antes, use:

```bash
python -m pip install --upgrade pip
```

---

### 🖼️ Passo 4 — (Opcional) Gerar o banner

O arquivo `assets/dashboard-cover.png` já está incluído no projeto. **Mas caso queira regenerá-lo** (por exemplo, se deletou por engano), basta executar:

```bash
python gerar_banner.py
```

Isso irá gerar novamente a imagem em `assets/dashboard-cover.png`.

> 💡 Se a imagem não existir, o dashboard ainda funciona — ele simplesmente mostra um emoji 📊 no lugar do banner.

---

### ▶️ Passo 5 — Executar o dashboard

Ainda com o ambiente virtual ativado, rode:

```bash
streamlit run app.py
```

Você verá uma saída no terminal parecida com:

```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

O navegador abrirá **automaticamente** em `http://localhost:8501` (isso está configurado em `.streamlit/config.toml` via `headless = false`).

Se por algum motivo o navegador não abrir, copie e cole o endereço `http://localhost:8501` manualmente.

---

### 🛑 Passo 6 — Encerrar o dashboard

Para parar a execução, volte ao terminal e pressione:

```
Ctrl + C
```

Para desativar o ambiente virtual, digite:

```bash
deactivate
```

---

## 🧭 Guia de Uso do Dashboard

Ao abrir o painel, você encontrará a seguinte estrutura:

### 🎛️ Barra Lateral (Sidebar)

1. **Filtros** — selecione período, tipo de Desenrola e UFs
2. **Outliers** — controle a remoção e a sensibilidade do IQR
3. **Botão Resetar** — limpa todos os filtros para o estado inicial

### 🗂️ Abas de Navegação

| Aba | Conteúdo |
|-----|----------|
| 📈 **Visão Geral** | Evolução mensal + Comparador de Períodos |
| 🏦 **Bancos** | Rankings + Scatter + Box Plot |
| 🗺️ **UFs** | Mapa do Brasil + distribuição geográfica |
| 🔬 **Outliers** | Diagnóstico completo e lista dos outliers removidos |

### 🔍 Comparador de Períodos

Na aba **Visão Geral**, você pode selecionar **dois intervalos de datas diferentes** (Período A e Período B) e comparar o desempenho lado a lado. ⚠️ Este comparador **sempre usa os dados brutos** (com outliers) e ignora o filtro de período da sidebar — isso é intencional, para permitir comparações justas sem interferência de filtros.

---

## 🔬 Metodologia de Tratamento de Outliers

### O que é o método IQR?

O **IQR (Intervalo Interquartílico)** é uma técnica estatística robusta para detecção de valores atípicos:

```
IQR = Q3 − Q1
Limite Inferior = Q1 − k × IQR
Limite Superior = Q3 + k × IQR
```

Onde:
- **Q1** = 1º quartil (25%)
- **Q3** = 3º quartil (75%)
- **k** = multiplicador de sensibilidade (padrão: 1.5)

Valores fora dos limites são classificados como **outliers**.

### Por que aplicar **por banco**?

Se aplicássemos o IQR globalmente, bancos como **Bradesco**, **Itaú** e **Santander** — que naturalmente operam volumes altíssimos — teriam **quase todas** as suas operações marcadas como outliers. Isso distorceria completamente a análise.

A solução adotada foi **calcular o IQR dentro de cada banco separadamente**, garantindo que cada instituição seja avaliada em relação ao **seu próprio padrão de operação**.

### Ajuste de sensibilidade

O usuário pode ajustar o multiplicador **k** na sidebar (entre **1.0** e **3.0**):

| Valor de k | Comportamento |
|------------|---------------|
| **1.0** | Mais agressivo — remove mais registros |
| **1.5** | Padrão estatístico clássico (Tukey) |
| **3.0** | Conservador — remove apenas extremos |

---

## 💡 Principais Insights Extraídos

- 🗺️ **Concentração geográfica**: SP, RJ e MG respondem pela maior parte do volume financeiro, refletindo o peso econômico dessas regiões.
- 💎 **Perfil dos bancos**:
  - **BTG Pactual** e **Votorantim** → ticket médio **alto** com poucas operações (alta renda)
  - **Nubank** e **Inter** → ticket médio **baixo** com **alto volume** (varejo)
- 📈 **Nova fase do programa**: há um **salto expressivo no volume** a partir de **maio/2025**, quando começam a surgir registros com o sufixo **PRUDENCIAL** — indicando uma nova etapa operacional do Desenrola Brasil.

---

## 🗃️ Sobre os Dados

### Colunas originais do CSV

| Coluna | Descrição |
|--------|-----------|
| `DATA_BASE` | Período no formato `AAAAMM` (ex: `202309`) |
| `TIPO_DESENROLA` | Tipo do programa (1, 2 ou 3) |
| `UNIDADE_FEDERACAO` | Sigla da UF (ex: `SP`, `RJ`) |
| `COD_CONGLOMERADO_FINANCEIRO` | Código do conglomerado bancário |
| `NOME_CONGLOMERADO_FINANCEIRO` | Nome do banco |
| `NUMERO_OPERACOES` | Quantidade de operações no período |
| `VOLUME_OPERACOES` | Volume financeiro total (R$) |

### Transformações aplicadas no `data_loader.py`

1. Conversão de `DATA_BASE` (AAAAMM) → `datetime`
2. Renomeação das colunas para nomes amigáveis em minúsculo
3. Criação da flag `is_prudencial` (indica registros da nova fase)
4. Criação da coluna `banco_limpo` (remove o sufixo "- PRUDENCIAL")
5. Remoção de registros com `volume <= 0`

---

## ❓ Solução de Problemas (FAQ)

<details>
<summary><b>O navegador não abre automaticamente</b></summary>

Verifique se `headless = false` está definido em `.streamlit/config.toml`. Se ainda não funcionar, acesse manualmente `http://localhost:8501`.
</details>

<details>
<summary><b>Erro: "Port 8501 is already in use"</b></summary>

Outra instância do Streamlit está rodando. Encerre-a com `Ctrl+C` no terminal correspondente ou rode em outra porta:

```bash
streamlit run app.py --server.port 8502
```
</details>

<details>
<summary><b>O mapa do Brasil não aparece</b></summary>

O mapa depende de um GeoJSON hospedado no GitHub. Se você estiver **offline** ou com restrições de rede, o dashboard exibirá automaticamente um **gráfico de barras alternativo** — isso é esperado e não é um bug.
</details>

<details>
<summary><b>Erro ao ativar o ambiente virtual no PowerShell</b></summary>

Execute uma vez:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Depois tente ativar novamente.
</details>

<details>
<summary><b>Erro "ModuleNotFoundError: No module named 'src'"</b></summary>

Certifique-se de estar executando o Streamlit a partir da **raiz do projeto** (onde está o `app.py`). O comando correto é:

```bash
streamlit run app.py
```

E **não**:

```bash
cd src && streamlit run ../app.py
```
</details>

---

## 📸 Preview do Dashboard

<div align="center">

| Seção | Descrição |
|-------|-----------|
| 🎯 **Topbar Ticker** | KPIs principais em destaque |
| 📈 **Visão Geral** | Evolução temporal interativa |
| 🏦 **Bancos** | Rankings em cards + gráficos comparativos |
| 🗺️ **UFs** | Mapa do Brasil colorido por volume |
| 🔬 **Outliers** | Diagnóstico transparente e auditável |

</div>

---

## 🤝 Contribuições

Este é um projeto **acadêmico individual**, desenvolvido especificamente para a Atividade II da disciplina de Análise e Visualização de Dados da CESAR School. Não está aberto para contribuições externas.

---

## 📄 Licença

Projeto de uso **acadêmico e educacional**. Dados públicos do programa **Desenrola Brasil**.

---

<div align="center">

**Desenvolvido por Felipe Alexandre Alves da Silva**

*Análise e Visualização de Dados · CESAR School · 2026*

</div>