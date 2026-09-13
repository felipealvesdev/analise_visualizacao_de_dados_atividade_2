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
    "#4a7c7e", "#7ba8a5", "#a8c5c2", "#c9d6d0",
    "#d4b483", "#e8c9a0", "#c28a7d", "#a86f5c",
    "#8899a6", "#6e7f8d", "#b4a7c9", "#8e7fa8", "#e0a5a5",
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


@st.cache_data(ttl=3600, show_spinner=False)
def carregar_geojson_brasil():
    """Baixa o GeoJSON dos estados brasileiros. Retorna None se offline."""
    import urllib.request
    import json as json_lib
    url = (
        "https://raw.githubusercontent.com/codeforamerica/"
        "click_that_hood/master/public/data/brazil-states.geojson"
    )
    try:
        with urllib.request.urlopen(url, timeout=8) as resp:
            return json_lib.loads(resp.read().decode("utf-8"))
    except Exception:
        return None


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


# ------------------------------------------------------------
# 🔢 FORMATADORES BRASILEIROS
# ------------------------------------------------------------
def fmt_int(val) -> str:
    """Formata inteiro com separador de milhar brasileiro (1.234.567)."""
    try:
        return f"{int(val):,}".replace(",", ".")
    except (ValueError, TypeError):
        return str(val)


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


def fmt_pct(val: float, decimals: int = 1, com_sinal: bool = False) -> str:
    """Formata percentual com vírgula decimal brasileira (13,93%)."""
    s = f"{val:+.{decimals}f}" if com_sinal else f"{val:.{decimals}f}"
    return s.replace(".", ",") + "%"


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
        rangemode='tozero',
    )
    if altura:
        fig.update_layout(height=altura)
    return fig


def render_ranking_card(titulo: str, icone: str, dados: list, label_fn, sub_fn, value_fn) -> str:
    """Gera o HTML de um card de ranking."""
    rows_html = ""
    for idx, row in enumerate(dados):
        rank_idx = idx + 1
        rank_class = "rank-num" if rank_idx <= 3 else "rank-num rank-num-muted"
        rows_html += f"""<div class="ranking-row">
            <div style="display:flex; align-items:center;">
                <span class="{rank_class}">#{rank_idx}</span>
                <div class="asset-info">
                    <span class="asset-code">{label_fn(row)}</span>
                    <span class="asset-name">{sub_fn(row)}</span>
                </div>
            </div>
            <div class="asset-value">{value_fn(row)}</div>
        </div>"""

    return f"""<div class="ranking-card">
        <div class="ranking-header">
            <div class="ranking-icon">{icone}</div>
            <div class="ranking-title">{titulo}</div>
        </div>
        {rows_html}
    </div>"""


# ============================================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Desenrola Brasil — Painel",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stPlotlyChart { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 2. CSS CUSTOMIZADO
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
.ranking-card:hover { box-shadow: 0 6px 16px rgba(74, 124, 126, 0.12); }

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

df_comp_base = df_full[df_full['tipo'].isin(tipos_sel)].copy()
if ufs_sel:
    df_comp_base = df_comp_base[df_comp_base['uf'].isin(ufs_sel)]

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

# ✅ Números formatados corretamente
topbar_html = f"""<div class="ticker-bar">
<div class="ticker-item">
<span class="ticker-label">VOLUME TOTAL</span>
<span class="ticker-value">{fmt_brl(vol_total)}</span>
</div>
<div class="ticker-item">
<span class="ticker-label">OPERAÇÕES</span>
<span class="ticker-value">{fmt_int(op_total)}</span>
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
<span class="ticker-value">{fmt_int(resumo['n_outliers'])} ({fmt_pct(resumo['pct_outliers'], 2)})</span>
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
col1.metric("Registros", fmt_int(len(df)))
col2.metric("Outliers", fmt_int(resumo['n_outliers']),
            delta=fmt_pct(resumo['pct_outliers'], 2), delta_color="inverse")
col3.metric("Volume Total", fmt_brl(vol_total))
col4.metric("Operações", fmt_int(op_total))

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
    # ✅ Pré-formatar para o hover
    agg_tempo_top['volume_fmt'] = agg_tempo_top['volume'].apply(fmt_brl)

    fig_linha = px.line(
        agg_tempo_top, x='data', y='volume', color='banco_limpo',
        markers=True,
        custom_data=['volume_fmt'],
        labels={'data': 'Mês', 'volume': 'Volume (R$)', 'banco_limpo': 'Banco'},
    )

    fig_linha.update_traces(
        hovertemplate="<b>%{customdata[0]}</b>",
        line=dict(width=2.5),
        marker=dict(size=6),
    )

    fig_linha.update_layout(
        hovermode='x unified',
        legend_title_text='',
    )

    fig_linha = estilizar_fig(fig_linha, altura=450)

    if not agg_tempo_top.empty:
        data_min_c = agg_tempo_top['data'].min()
        data_max_c = agg_tempo_top['data'].max()
        padding = pd.Timedelta(days=5)
        fig_linha.update_xaxes(
            range=[data_min_c - padding, data_max_c + padding]
        )

    st.plotly_chart(fig_linha, use_container_width=True)

    st.info(
        "💡 **Insight**: há um salto visível no volume a partir de maio/2025, "
        "quando começam a aparecer os registros com sufixo *PRUDENCIAL*, "
        "indicando nova fase do programa."
    )

    # ----------------------------------------------------------
    # COMPARADOR DE PERÍODOS
    # ----------------------------------------------------------
    st.markdown("---")
    st.subheader("🔍 Comparador de Períodos")
    st.caption(
        "Compare o desempenho entre dois recortes de tempo. "
        "Este comparador **ignora o filtro de período** da barra lateral — "
        "usa todo o histórico disponível (respeitando Tipo e UF)."
    )

    with st.container():
        col_p1, col_p2 = st.columns(2)

        data_min_comp = df_comp_base['data'].min().date()
        data_max_comp = df_comp_base['data'].max().date()

        default_a_start = data_min_comp
        default_a_end = (pd.Timestamp(data_min_comp) + pd.DateOffset(months=11)).date()
        if default_a_end > data_max_comp:
            default_a_end = data_max_comp

        default_b_end = data_max_comp
        default_b_start = (pd.Timestamp(data_max_comp) - pd.DateOffset(months=11)).date()
        if default_b_start < data_min_comp:
            default_b_start = data_min_comp

        with col_p1:
            st.markdown("##### 🅰️ Período A")
            p1_start = st.date_input(
                "Início A",
                value=default_a_start,
                min_value=data_min_comp,
                max_value=data_max_comp,
                key="p1_start",
            )
            p1_end = st.date_input(
                "Fim A",
                value=default_a_end,
                min_value=p1_start,
                max_value=data_max_comp,
                key="p1_end",
            )

        with col_p2:
            st.markdown("##### 🅱️ Período B")
            p2_start = st.date_input(
                "Início B",
                value=default_b_start,
                min_value=data_min_comp,
                max_value=data_max_comp,
                key="p2_start",
            )
            p2_end = st.date_input(
                "Fim B",
                value=default_b_end,
                min_value=p2_start,
                max_value=data_max_comp,
                key="p2_end",
            )

        df_p1 = df_comp_base[
            (df_comp_base['data'] >= pd.to_datetime(p1_start)) &
            (df_comp_base['data'] <= pd.to_datetime(p1_end))
        ]
        df_p2 = df_comp_base[
            (df_comp_base['data'] >= pd.to_datetime(p2_start)) &
            (df_comp_base['data'] <= pd.to_datetime(p2_end))
        ]

        vol_p1 = df_p1['volume'].sum()
        vol_p2 = df_p2['volume'].sum()
        op_p1 = df_p1['operacoes'].sum()
        op_p2 = df_p2['operacoes'].sum()

        delta_vol = ((vol_p2 - vol_p1) / vol_p1 * 100) if vol_p1 else 0
        delta_op = ((op_p2 - op_p1) / op_p1 * 100) if op_p1 else 0

        # ✅ Métricas com formatação brasileira
        st.markdown("#### 📊 Resultado da Comparação")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Volume A", fmt_brl(vol_p1))
        m2.metric("Volume B", fmt_brl(vol_p2), delta=fmt_pct(delta_vol, 1, com_sinal=True))
        m3.metric("Operações A", fmt_int(op_p1))
        m4.metric("Operações B", fmt_int(op_p2), delta=fmt_pct(delta_op, 1, com_sinal=True))

        # ✅ Gráfico comparativo com hover formatado
        st.markdown("##### 📈 Evolução lado a lado")
        df_p1_agg = (
            df_p1.groupby('data', as_index=False)['volume'].sum()
            .rename(columns={'volume': 'Volume'})
            .assign(Período='🅰️ Período A')
        )
        df_p2_agg = (
            df_p2.groupby('data', as_index=False)['volume'].sum()
            .rename(columns={'volume': 'Volume'})
            .assign(Período='🅱️ Período B')
        )
        df_p1_agg['mes_relativo'] = df_p1_agg.groupby('Período').cumcount() + 1
        df_p2_agg['mes_relativo'] = df_p2_agg.groupby('Período').cumcount() + 1
        df_comp_plot = pd.concat([df_p1_agg, df_p2_agg], ignore_index=True)

        if not df_comp_plot.empty:
            df_comp_plot['Volume_fmt'] = df_comp_plot['Volume'].apply(fmt_brl)

            fig_comp = px.line(
                df_comp_plot,
                x='mes_relativo', y='Volume', color='Período',
                markers=True,
                custom_data=['Volume_fmt'],
                labels={'mes_relativo': 'Mês do período', 'Volume': 'Volume (R$)'},
                color_discrete_map={
                    '🅰️ Período A': '#4a7c7e',
                    '🅱️ Período B': '#c28a7d',
                },
            )
            fig_comp.update_traces(
                hovertemplate="<b>%{customdata[0]}</b>",
                line=dict(width=2.5),
                marker=dict(size=8),
            )
            fig_comp.update_layout(
                hovermode='x unified',
                legend_title_text='',
            )
            fig_comp = estilizar_fig(fig_comp, altura=380)
            st.plotly_chart(fig_comp, use_container_width=True)

        # ✅ Insight com percentual brasileiro
        if delta_vol > 0:
            st.success(
                f"📈 O **Período B** teve um crescimento de **{fmt_pct(delta_vol, 1, com_sinal=True)}** "
                f"em volume em relação ao **Período A**."
            )
        elif delta_vol < 0:
            st.warning(
                f"📉 O **Período B** teve uma queda de **{fmt_pct(delta_vol, 1, com_sinal=True)}** "
                f"em volume em relação ao **Período A**."
            )
        else:
            st.info("Os dois períodos têm volumes equivalentes.")

# ---------- ABA 2 ----------
with tab2:
    st.subheader("🏆 Rankings Comparativos")
    st.caption("Top 8 bancos e UFs por volume e operações. Reflita o comportamento das instituições.")

    r1, r2, r3 = st.columns(3)

    # Ranking 1 — Top 8 bancos por volume
    ranking_vol = (
        df_tratado.groupby('banco_limpo', as_index=False)
        .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
        .nlargest(8, 'volume')
    )

    with r1:
        card = render_ranking_card(
            titulo="Top 8 Bancos por Volume",
            icone="💎",
            dados=ranking_vol.to_dict('records'),
            label_fn=lambda r: r['banco_limpo'][:20],
            sub_fn=lambda r: f"{fmt_int(r['operacoes'])} operações",  # ✅
            value_fn=lambda r: fmt_brl(r['volume']),
        )
        st.markdown(card, unsafe_allow_html=True)

    # Ranking 2 — Top 8 bancos por operações
    ranking_ops = (
        df_tratado.groupby('banco_limpo', as_index=False)
        .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
        .nlargest(8, 'operacoes')
    )

    with r2:
        card = render_ranking_card(
            titulo="Top 8 Bancos por Operações",
            icone="🔢",
            dados=ranking_ops.to_dict('records'),
            label_fn=lambda r: r['banco_limpo'][:20],
            sub_fn=lambda r: fmt_brl(r['volume']),
            value_fn=lambda r: fmt_int(r['operacoes']),  # ✅
        )
        st.markdown(card, unsafe_allow_html=True)

    # Ranking 3 — Top 8 UFs por volume
    ranking_uf = agrupar_uf(df_tratado).nlargest(8, 'volume')

    with r3:
        card = render_ranking_card(
            titulo="Top 8 UFs por Volume",
            icone="🗺️",
            dados=ranking_uf.to_dict('records'),
            label_fn=lambda r: r['uf'],
            sub_fn=lambda r: f"{fmt_int(r['operacoes'])} operações",  # ✅
            value_fn=lambda r: fmt_brl(r['volume']),
        )
        st.markdown(card, unsafe_allow_html=True)

    # ----------------------------------------------------------
    # Scatter + Box plot
    # ----------------------------------------------------------
    st.markdown("---")
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.subheader("Ticket Médio × Nº de Operações")
        df_ticket = (
            df_tratado.groupby('banco_limpo', as_index=False)
            .agg(volume=('volume', 'sum'), operacoes=('operacoes', 'sum'))
        )
        df_ticket['ticket_medio'] = df_ticket['volume'] / df_ticket['operacoes']
        df_ticket = df_ticket[df_ticket['operacoes'] > 0]

        # ✅ Pré-formatar para o hover
        df_ticket['banco_fmt'] = df_ticket['banco_limpo']
        df_ticket['volume_fmt'] = df_ticket['volume'].apply(fmt_brl)
        df_ticket['operacoes_fmt'] = df_ticket['operacoes'].apply(fmt_int)
        df_ticket['ticket_fmt'] = df_ticket['ticket_medio'].apply(fmt_brl)

        fig_scatter = px.scatter(
            df_ticket, x='operacoes', y='ticket_medio',
            size='volume', color='banco_limpo',
            custom_data=['banco_fmt', 'operacoes_fmt', 'ticket_fmt', 'volume_fmt'],
            labels={'operacoes': 'Nº de Operações', 'ticket_medio': 'Ticket Médio (R$)'},
        )
        fig_scatter.update_traces(
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Volume: %{customdata[3]}<br>"
                "Operações: %{customdata[1]}<br>"
                "Ticket Médio: %{customdata[2]}<extra></extra>"
            )
        )
        fig_scatter.update_layout(showlegend=False)
        fig_scatter = estilizar_fig(fig_scatter, altura=420)
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_b:
        st.subheader("Distribuição do Volume (Box Plot)")
        st.caption("Mediana, quartis e outliers naturais por banco.")
        top8_nomes = ranking_vol['banco_limpo'].tolist()
        df_box = df[df['banco_limpo'].isin(top8_nomes)].copy()
        df_box['volume_fmt'] = df_box['volume'].apply(fmt_brl)

        fig_box = px.box(
            df_box, x='banco_limpo', y='volume', color='banco_limpo',
            custom_data=['volume_fmt'],
            labels={'banco_limpo': '', 'volume': 'Volume (R$)'}
        )
        fig_box.update_traces(
            hovertemplate="<b>%{customdata[0]}</b><extra></extra>"
        )
        fig_box.update_layout(showlegend=False, xaxis_tickangle=-30)
        fig_box = estilizar_fig(fig_box, altura=420)
        escuro = tema_atual_eh_escuro()
        cor_eixo = "#e8f0ef" if escuro else "#2c3e3f"
        fig_box.update_xaxes(tickfont=dict(color=cor_eixo, size=10))
        fig_box.update_yaxes(tickfont=dict(color=cor_eixo, size=10))
        st.plotly_chart(fig_box, use_container_width=True)

    st.info(
        "💡 **Insight**: bancos como **BTG Pactual** e **Votorantim** têm ticket médio alto "
        "com poucas operações (alta renda), enquanto **Nubank** e **Inter** têm ticket "
        "médio baixo com alto volume (varejo)."
    )

# ---------- ABA 3 ----------
with tab3:
    st.subheader("Distribuição Geográfica do Volume")
    st.caption("Volume financeiro agregado por Unidade Federativa.")

    agg_uf = agrupar_uf(df_tratado)
    # ✅ Pré-formatar para o hover
    agg_uf['volume_fmt'] = agg_uf['volume'].apply(fmt_brl)
    agg_uf['operacoes_fmt'] = agg_uf['operacoes'].apply(fmt_int)

    geojson_br = carregar_geojson_brasil()

    if geojson_br is not None:
        try:
            fig_mapa = px.choropleth(
                agg_uf,
                geojson=geojson_br,
                locations='uf',
                featureidkey='properties.sigla',
                color='volume',
                color_continuous_scale=[
                    "#f0efe8", "#c9d6d0", "#a8c5c2", "#7ba8a5", "#4a7c7e"
                ],
                labels={'volume': 'Volume (R$)', 'uf': 'UF'},
                custom_data=['volume_fmt', 'operacoes_fmt'],
            )
            # ✅ Hover com formato brasileiro
            fig_mapa.update_traces(
                hovertemplate=(
                    "<b>%{location}</b><br>"
                    "Volume: %{customdata[0]}<br>"
                    "Operações: %{customdata[1]}<extra></extra>"
                )
            )
            fig_mapa.update_geos(
                fitbounds="locations",
                visible=False,
                bgcolor="rgba(0,0,0,0)",
                showcountries=False,
                showcoastlines=False,
                showland=False,
            )
            fig_mapa.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                height=520,
                coloraxis_colorbar=dict(
                    title="Volume",
                    tickfont=dict(color=COR_TEXTO),
                    title_font=dict(color=COR_TEXTO),
                ),
            )
            fig_mapa = estilizar_fig(fig_mapa, altura=520)
            fig_mapa.update_layout(
                margin=dict(l=0, r=0, t=20, b=0),
                coloraxis_showscale=True,
            )
            st.plotly_chart(fig_mapa, use_container_width=True)
        except Exception as e:
            st.warning(f"⚠️ Não foi possível renderizar o mapa: {e}")
            geojson_br = None

    if geojson_br is None:
        st.info(
            "💡 **Mapa indisponível** (sem conexão ou GeoJSON inacessível). "
            "Mostrando gráfico de barras alternativo."
        )
        fig_uf = px.bar(
            agg_uf, x='uf', y='volume',
            custom_data=['volume_fmt', 'operacoes_fmt'],
            labels={'uf': 'UF', 'volume': 'Volume (R$)'},
            color='volume',
            color_continuous_scale=["#f0efe8", "#a8c5c2", "#7ba8a5", "#4a7c7e"],
        )
        fig_uf.update_traces(
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Volume: %{customdata[0]}<br>"
                "Operações: %{customdata[1]}<extra></extra>"
            )
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
    col_m1.metric("Outliers detectados", fmt_int(resumo['n_outliers']))
    col_m2.metric("Média (com outliers)", fmt_brl(resumo['media_com_outliers']))
    col_m3.metric("Média (sem outliers)", fmt_brl(resumo['media_sem_outliers']))

    st.markdown(
        f"""
        **Método:** IQR com multiplicador **{str(multiplicador).replace('.', ',')}**, calculado dentro de cada banco.
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
        .copy()
    )
    # ✅ Formatando a tabela com padrão brasileiro
    top_out['data'] = pd.to_datetime(top_out['data']).dt.strftime('%m/%Y')
    top_out['operacoes'] = top_out['operacoes'].apply(fmt_int)
    top_out['volume'] = top_out['volume'].apply(fmt_brl)
    top_out.columns = ['Mês', 'UF', 'Banco', 'Operações', 'Volume']
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