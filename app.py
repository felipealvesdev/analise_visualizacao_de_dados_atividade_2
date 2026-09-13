import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.io as pio
from PIL import Image
from src.data_loader import load_data
from src.outliers import detectar_outliers_iqr, resumo_outliers


# ============================================================
# PALETAS PASTEL FINANCEIRAS
# ============================================================
PALETA_FINANCEIRA = [
    "#4a7c7e",  # verde-petróleo suave
    "#7ba8a5",  # verde-menta
    "#a8c5c2",  # verde-água pastel
    "#c9d6d0",  # cinza-esverdeado claro
    "#d4b483",  # areia dourada
    "#e8c9a0",  # bege quente
    "#c28a7d",  # terracota suave
    "#a86f5c",  # marrom suave
    "#8899a6",  # azul-acinzentado
    "#6e7f8d",  # azul-petróleo escuro
    "#b4a7c9",  # lavanda pastel
    "#8e7fa8",  # roxo suave
    "#e0a5a5",  # rosa antigo
]

COR_PRIMARIA = "#4a7c7e"
COR_TEXTO = "#2c3e3f"
COR_TEXTO_SUAVE = "#6b7c7d"
COR_POSITIVA = "#5a9a7a"
COR_NEGATIVA = "#c47a7a"


# ============================================================
# FUNÇÕES AUXILIARES (com cache)
# ============================================================
@st.cache_data(ttl=3600)
def carregar_banner():
    img = Image.open("assets/dashboard-cover.png")
    img.verify()
    return Image.open("assets/dashboard-cover.png")


@st.cache_data(ttl=600)
def agrupar_tempo(df: pd.DataFrame, top_n: int = 8) -> pd.DataFrame:
    agg = df.groupby(['data', 'banco_limpo'], as_index=False)['volume'].sum()
    top = df.groupby('banco_limpo')['volume'].sum().nlargest(top_n).index.tolist()
    return agg[agg['banco_limpo'].isin(top)]


@st.cache_data(ttl=600)
def agrupar_uf(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby('uf', as_index=False)
        .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
        .sort_values('volume', ascending=False)
    )


def fmt_brl(val: float) -> str:
    """Formata valor em Real brasileiro (R$ 1.234,56 / R$ 12,34 B)."""
    if val >= 1e9:
        s = f"{val/1e9:,.2f} B"
    elif val >= 1e6:
        s = f"{val/1e6:,.2f} M"
    elif val >= 1e3:
        s = f"{val/1e3:,.2f} K"
    else:
        s = f"{val:,.2f}"
    return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")


def tema_atual_eh_escuro() -> bool:
    """Detecta se o Streamlit está em modo escuro."""
    try:
        base = st.get_option("theme.base")
        if base is not None:
            return base == "dark"
        return st.context.theme.type == "dark"
    except Exception:
        return False


def estilizar_fig(fig, altura=None):
    """Aplica paleta pastel e ajusta cores conforme o tema atual (claro/escuro)."""
    escuro = tema_atual_eh_escuro()

    if escuro:
        cor_texto = "#e8f0ef"
        cor_grid = "rgba(168, 197, 194, 0.12)"
        cor_hover_bg = "#1e2628"
        cor_hover_text = "#e8f0ef"
        cor_legenda_bg = "rgba(30, 38, 40, 0.85)"
        cor_legenda_borda = "rgba(122, 168, 165, 0.3)"
    else:
        cor_texto = "#2c3e3f"
        cor_grid = "rgba(122, 168, 165, 0.18)"
        cor_hover_bg = "#fafaf7"
        cor_hover_text = "#2c3e3f"
        cor_legenda_bg = "rgba(250, 250, 247, 0.9)"
        cor_legenda_borda = "rgba(74, 124, 126, 0.2)"

    fig.update_layout(
        colorway=PALETA_FINANCEIRA,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="sans-serif", size=12, color=cor_texto),
        # Margens generosas para o popup do hover não ser cortado
        margin=dict(l=60, r=40, t=40, b=60),
        hoverlabel=dict(
            bgcolor=cor_hover_bg,
            bordercolor=cor_legenda_borda,
            font=dict(size=12, family="sans-serif", color=cor_hover_text),
            namelength=-1,
        ),
        legend=dict(
            bgcolor=cor_legenda_bg,
            bordercolor=cor_legenda_borda,
            borderwidth=1,
            font=dict(color=cor_texto, size=11),
        ),
    )
    fig.update_layout(title=None, title_text="")
    fig.update_xaxes(
        gridcolor=cor_grid,
        tickfont=dict(color=cor_texto),
        title_font=dict(color=cor_texto),
        zerolinecolor=cor_grid,
        linecolor=cor_grid,
        rangebreaks=[],
        tickmode='auto',
        nticks=10,
    )
    fig.update_yaxes(
        gridcolor=cor_grid,
        tickfont=dict(color=cor_texto),
        title_font=dict(color=cor_texto),
        zerolinecolor=cor_grid,
        linecolor=cor_grid,
        # Força o eixo Y a começar no zero
        rangemode='tozero',
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Desenrola Brasil — Painel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Força o container do Plotly a usar 100% da largura disponível
st.markdown("""
<style>
    .stPlotlyChart { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. CSS CUSTOMIZADO (adapta ao tema claro/escuro)
# ============================================================
st.markdown("""
<style>
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 2rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

.ticker-bar {
    background: linear-gradient(90deg, #4a7c7e 0%, #6e9b9d 100%);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 14px 20px;
    margin: -1rem -2rem 2rem -2rem;
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    border-radius: 0 0 12px 12px;
    box-shadow: 0 2px 8px rgba(74, 124, 126, 0.15);
}

.ticker-item {
    font-size: 0.9rem;
    font-weight: 600;
    display: flex;
    gap: 8px;
    align-items: center;
}

.ticker-label { color: #d4e8e6; font-weight: 500; }
.ticker-value { color: #ffffff; font-weight: 700; }

.ranking-card {
    background: #ffffff;
    border-radius: 12px;
    border: 1px solid rgba(74, 124, 126, 0.15);
    box-shadow: 0 4px 12px rgba(74, 124, 126, 0.06);
    overflow: hidden;
    transition: box-shadow 0.2s ease;
}
.ranking-card:hover {
    box-shadow: 0 6px 16px rgba(74, 124, 126, 0.12);
}

.ranking-header {
    background: linear-gradient(180deg, #f0efe8 0%, #e8e7de 100%);
    text-align: center;
    padding: 16px 12px;
    border-bottom: 1px solid rgba(74, 124, 126, 0.1);
}

.ranking-icon { font-size: 1.4rem; margin-bottom: 4px; }
.ranking-title { font-weight: 600; font-size: 0.95rem; color: #2c3e3f; }

.ranking-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 16px;
    border-bottom: 1px solid rgba(74, 124, 126, 0.08);
    color: #2c3e3f;
}
.ranking-row:last-child { border-bottom: none; }

.rank-num {
    font-weight: 700;
    font-size: 0.85rem;
    color: #b58a3c;
    width: 28px;
}
.rank-num-muted { color: #a8b3b3; }

.asset-info { flex: 1; display: flex; flex-direction: column; margin-left: 8px; }
.asset-code { font-weight: 700; font-size: 0.85rem; color: #2c3e3f; }
.asset-name { font-size: 0.72rem; color: #6b7c7d; }
.asset-value { font-weight: 600; font-size: 0.85rem; color: #4a7c7e; }

[data-theme="dark"] .ranking-card {
    background: #1e2628;
    border-color: rgba(122, 168, 165, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
[data-theme="dark"] .ranking-header {
    background: linear-gradient(180deg, #252f32 0%, #1e2628 100%);
    border-bottom-color: rgba(122, 168, 165, 0.15);
}
[data-theme="dark"] .ranking-title { color: #d4e8e6; }
[data-theme="dark"] .ranking-row {
    color: #d4e8e6;
    border-bottom-color: rgba(122, 168, 165, 0.1);
}
[data-theme="dark"] .asset-code { color: #e8f0ef; }
[data-theme="dark"] .asset-name { color: #8fa5a5; }
[data-theme="dark"] .asset-value { color: #7ba8a5; }
[data-theme="dark"] .rank-num { color: #e8c98a; }
[data-theme="dark"] .rank-num-muted { color: #5e7070; }

[data-theme="dark"] .ticker-bar {
    background: linear-gradient(90deg, #2c4a4c 0%, #3d6365 100%);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}
[data-theme="dark"] .ticker-label { color: #a8c5c2; }

[data-theme="dark"] .stAlert {
    background-color: rgba(122, 168, 165, 0.08);
    border-color: rgba(122, 168, 165, 0.25);
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# 3. CARREGAMENTO DOS DADOS
# ============================================================
df_full = load_data()

if "reset_key" not in st.session_state:
    st.session_state.reset_key = 0

# ============================================================
# 4. SIDEBAR — WIDGETS
# ============================================================
with st.sidebar:
    st.header("🔎 Filtros")

    data_min, data_max = df_full['data'].min(), df_full['data'].max()
    periodo = st.slider(
        "Período:",
        min_value=data_min.to_pydatetime(),
        max_value=data_max.to_pydatetime(),
        value=(data_min.to_pydatetime(), data_max.to_pydatetime()),
        format="MM/YYYY",
        key=f"periodo_{st.session_state.reset_key}"
    )

    tipos = sorted(df_full['tipo'].unique())
    tipos_sel = st.pills(
        "Tipo Desenrola:",
        options=tipos,
        default=tipos,
        selection_mode="multi",
        key=f"pills_{st.session_state.reset_key}"
    )

    ufs = sorted(df_full['uf'].unique())
    ufs_sel = st.multiselect(
        "UF:",
        ufs,
        default=ufs,
        key=f"ufs_{st.session_state.reset_key}"
    )

    st.divider()
    st.subheader("⚙️ Outliers")
    remover_outliers = st.toggle(
        "Remover outliers (IQR por banco)",
        value=True,
        help="IQR dentro de cada banco — evita penalizar grandes instituições.",
        key=f"toggle_outliers_{st.session_state.reset_key}"
    )
    multiplicador = st.slider(
        "Sensibilidade IQR:",
        min_value=1.0, max_value=3.0, value=1.5, step=0.1,
        key=f"mult_{st.session_state.reset_key}"
    )

    st.divider()
    if st.button("🔄 Resetar todos os filtros", use_container_width=True):
        st.session_state.reset_key += 1
        st.rerun()

# ============================================================
# 5. FILTRAGEM
# ============================================================
if not tipos_sel:
    st.markdown("---")
    st.error(
        "⚠️ **Nenhum Tipo Desenrola selecionado.**\n\n"
        "Use os botões **1**, **2** ou **3** na barra lateral esquerda para "
        "escolher pelo menos um tipo de operação do programa."
    )
    st.info(
        "💡 **Dica:** clique em um dos botões de tipo na barra lateral. "
        "Se quiser começar do zero, clique no botão abaixo."
    )
    if st.button("🔄 Resetar filtros", type="primary"):
        st.session_state.reset_key += 1
        st.rerun()
    st.stop()

df = df_full[
    (df_full['data'] >= periodo[0]) &
    (df_full['data'] <= periodo[1]) &
    (df_full['tipo'].isin(tipos_sel))
].copy()

if ufs_sel:
    df = df[df['uf'].isin(ufs_sel)]

if df.empty:
    st.markdown("---")
    st.error(
        "⚠️ **Nenhum dado corresponde aos filtros selecionados.**\n\n"
        "Tente ampliar o período ou selecionar mais UFs na barra lateral."
    )
    if st.button("🔄 Resetar filtros", type="primary"):
        st.session_state.reset_key += 1
        st.rerun()
    st.stop()

# ============================================================
# 6. OUTLIERS
# ============================================================
mascara_out = detectar_outliers_iqr(
    df, coluna='volume', agrupar_por=['banco_limpo'],
    multiplicador=multiplicador
)
resumo = resumo_outliers(df, 'volume', mascara_out)
df_tratado = df.loc[~mascara_out].copy() if remover_outliers else df.copy()

# ============================================================
# 7. TOPBAR TICKER
# ============================================================
vol_total = df_tratado['volume'].sum()
op_total = df_tratado['operacoes'].sum()
ticket_medio = vol_total / op_total if op_total else 0
uf_top = (
    df_tratado.groupby('uf')['volume'].sum().idxmax()
    if len(df_tratado) > 0 else "—"
)
banco_top = (
    df_tratado.groupby('banco_limpo')['volume'].sum().idxmax()
    if len(df_tratado) > 0 else "—"
)

topbar_html = f"""<div class="ticker-bar">
<div class="ticker-item">
<span class="ticker-label">VOLUME TOTAL</span>
<span class="ticker-value">{fmt_brl(vol_total)}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">OPERAÇÕES</span>
<span class="ticker-value">{op_total:,.0f}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">TICKET MÉDIO</span>
<span class="ticker-value">{fmt_brl(ticket_medio)}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">UF LÍDER</span>
<span class="ticker-value">{uf_top}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">BANCO LÍDER</span>
<span class="ticker-value">{banco_top}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">OUTLIERS</span>
<span class="ticker-value">{resumo['n_outliers']:,} ({resumo['pct_outliers']}%)</span>
</div>
</div>"""

st.markdown(topbar_html, unsafe_allow_html=True)

# ============================================================
# 8. HEADER
# ============================================================
col_logo, col_titulo = st.columns([1, 5])
with col_logo:
    try:
        img = carregar_banner()
        st.image(img, use_container_width=True)
    except Exception:
        st.markdown("<h1 style='font-size:3rem;'>📊</h1>", unsafe_allow_html=True)

with col_titulo:
    st.markdown(
        "<h1 style='margin:0; font-weight:700; color:#4a7c7e;'>Desenrola Brasil — Painel Analítico</h1>",
        unsafe_allow_html=True
    )
    st.markdown(
        "Análise do **volume financeiro** e do **número de operações** do programa "
        "por banco, UF e período, com **tratamento de outliers via IQR por banco**."
    )

# ============================================================
# 9. MÉTRICAS PRINCIPAIS
# ============================================================
st.markdown("---")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Registros", f"{len(df):,}")
col2.metric("Outliers", f"{resumo['n_outliers']:,}",
            delta=f"{resumo['pct_outliers']}%", delta_color="inverse")
col3.metric("Volume Total", fmt_brl(vol_total))
col4.metric("Operações", f"{op_total:,.0f}")

# ============================================================
# 10. ABAS
# ============================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Visão Geral", "🏦 Bancos", "🗺️ UFs", "🔬 Outliers"
])

# ---------- ABA 1 ----------
with tab1:
    st.subheader("Evolução Mensal do Volume")
    st.caption("Top 8 bancos por volume total. Use zoom e hover do Plotly para explorar.")

    agg_tempo_top = agrupar_tempo(df_tratado, top_n=8)

    fig_linha = px.line(
        agg_tempo_top, x='data', y='volume', color='banco_limpo',
        markers=True,
        labels={'data': 'Mês', 'volume': 'Volume (R$)', 'banco_limpo': 'Banco'},
    )

    # Hover limpo: no modo 'x unified' o nome do banco aparece à esquerda
    fig_linha.update_traces(
        hovertemplate="<b>R$ %{y:,.2f}</b>",
        line=dict(width=2.5),
        marker=dict(size=6),
    )

    fig_linha.update_layout(
        hovermode='x unified',
        legend_title_text='',
    )

    # Aplica paleta, margens e eixo Y começando em zero
    fig_linha = estilizar_fig(fig_linha, altura=450)

    # Remove o padding automático do eixo X (5 dias é imperceptível visualmente)
    if not agg_tempo_top.empty:
        data_min = agg_tempo_top['data'].min()
        data_max = agg_tempo_top['data'].max()
        padding = pd.Timedelta(days=5)
        fig_linha.update_xaxes(
            range=[data_min - padding, data_max + padding]
        )

    st.plotly_chart(fig_linha, use_container_width=True)

    st.info(
        "💡 **Insight**: há um salto visível no volume a partir de maio/2025, "
        "quando começam a aparecer os registros com sufixo *PRUDENCIAL*, "
        "indicando nova fase do programa."
    )

# ---------- ABA 2 ----------
with tab2:
    col_a, col_b = st.columns([1, 1])

    with col_a:
        ranking = (
            df_tratado.groupby('banco_limpo', as_index=False)
            .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
            .nlargest(8, 'volume')
        )

        rows_html = ""
        for idx, row in enumerate(ranking.to_dict('records')):
            rank_idx = idx + 1
            rank_class = "rank-num" if rank_idx <= 3 else "rank-num rank-num-muted"
            rows_html += f"""<div class="ranking-row">
                <div style="display:flex; align-items:center;">
                    <span class="{rank_class}">#{rank_idx}</span>
                    <div class="asset-info">
                        <span class="asset-code">{row['banco_limpo'][:20]}</span>
                        <span class="asset-name">{row['operacoes']:,} operações</span>
                    </div>
                </div>
                <div class="asset-value">{fmt_brl(row['volume'])}</div>
            </div>"""

        card_html = f"""<div class="ranking-card">
            <div class="ranking-header">
                <div class="ranking-icon">🏆</div>
                <div class="ranking-title">Top 8 Bancos por Volume</div>
            </div>
            {rows_html}
        </div>"""

        st.markdown(card_html, unsafe_allow_html=True)

    with col_b:
        st.subheader("Ticket Médio × Nº de Operações")
        df_ticket = (
            df_tratado.groupby('banco_limpo', as_index=False)
            .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
        )
        df_ticket['ticket_medio'] = df_ticket['volume'] / df_ticket['operacoes']
        df_ticket = df_ticket[df_ticket['operacoes'] > 0]

        fig_scatter = px.scatter(
            df_ticket, x='operacoes', y='ticket_medio',
            size='volume', color='banco_limpo', hover_name='banco_limpo',
            labels={'operacoes': 'Nº de Operações', 'ticket_medio': 'Ticket Médio (R$)'},
        )
        fig_scatter.update_layout(showlegend=False)
        fig_scatter = estilizar_fig(fig_scatter, altura=420)
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.info(
        "💡 **Insight**: bancos como **BTG Pactual** e **Votorantim** têm ticket médio alto "
        "com poucas operações (alta renda), enquanto **Nubank** e **Inter** têm ticket "
        "médio baixo com alto volume (varejo)."
    )

    st.subheader("Distribuição do Volume por Banco (Box Plot)")
    st.caption("Mostra mediana, quartis e outliers naturais — justifica a remoção.")

    top8_nomes = ranking['banco_limpo'].tolist()
    df_box = df[df['banco_limpo'].isin(top8_nomes)]
    fig_box = px.box(
        df_box, x='banco_limpo', y='volume', color='banco_limpo',
        labels={'banco_limpo': '', 'volume': 'Volume (R$)'}
    )
    fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
    fig_box = estilizar_fig(fig_box, altura=420)
    escuro = tema_atual_eh_escuro()
    cor_eixo = "#e8f0ef" if escuro else "#2c3e3f"
    fig_box.update_xaxes(tickfont=dict(color=cor_eixo, size=10))
    fig_box.update_yaxes(tickfont=dict(color=cor_eixo, size=10))
    st.plotly_chart(fig_box, use_container_width=True)

# ---------- ABA 3 ----------
with tab3:
    st.subheader("Volume e Operações por UF")
    agg_uf = agrupar_uf(df_tratado)

    fig_uf = px.bar(
        agg_uf, x='uf', y='volume',
        labels={'uf': 'UF', 'volume': 'Volume (R$)'},
        color='volume',
        color_continuous_scale=["#f0efe8", "#a8c5c2", "#7ba8a5", "#4a7c7e"],
    )
    fig_uf.update_layout(coloraxis_showscale=False)
    fig_uf = estilizar_fig(fig_uf, altura=420)
    st.plotly_chart(fig_uf, use_container_width=True)

    st.info(
        "💡 **Insight**: SP, RJ e MG concentram a maior parte do volume, "
        "refletindo o peso econômico desses estados no sistema financeiro."
    )

# ---------- ABA 4 ----------
with tab4:
    st.subheader("Diagnóstico de Outliers")

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Outliers detectados", f"{resumo['n_outliers']:,}")
    col_m2.metric("Média (com outliers)", fmt_brl(resumo['media_com_outliers']))
    col_m3.metric("Média (sem outliers)", fmt_brl(resumo['media_sem_outliers']))

    st.markdown(
        f"""
        **Método:** IQR com multiplicador **{multiplicador}**, calculado dentro de cada banco.
        Isso evita remover operações legítimas de instituições que naturalmente operam volumes maiores.

        | Métrica | Com outliers | Sem outliers |
        |---|---|---|
        | Volume máximo | {fmt_brl(resumo['max_com_outliers'])} | {fmt_brl(resumo['max_sem_outliers'])} |
        | Mediana | {fmt_brl(resumo['mediana'])} | — |
        """
    )

    st.markdown("#### Top 15 outliers removidos")
    top_out = (
        df.loc[mascara_out]
        .nlargest(15, 'volume')[['data', 'uf', 'banco_limpo', 'operacoes', 'volume']]
    )
    st.dataframe(top_out, use_container_width=True, hide_index=True)

# ============================================================
# 11. DOWNLOAD
# ============================================================
st.markdown("---")
with st.expander("🗂️ Ver e baixar dados filtrados"):
    st.dataframe(df_tratado, use_container_width=True, hide_index=True)
    csv = df_tratado.to_csv(index=False, sep=';', decimal=',').encode('utf-8')
    st.download_button(
        label="⬇️ Baixar CSV filtrado",
        data=csv,
        file_name="desenrola_filtrado.csv",
        mime="text/csv"
    )

st.markdown("---")
st.caption(
    "Dashboard desenvolvido para a Atividade II — Análise e Visualização de Dados | "
    "CESAR School | Plotly Express + Streamlit + tratamento de outliers por IQR."
)