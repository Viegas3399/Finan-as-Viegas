"""
App de Controle de Finanças Pessoais
=====================================

Um app simples para lançar receitas e despesas manualmente e acompanhar
tudo em um dashboard visual e dinâmico.

Este é o MVP (primeira versão funcional). Feito para rodar com Streamlit.
"""

from datetime import date, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from db import (
    CATEGORIAS_DESPESA,
    CATEGORIAS_RECEITA,
    add_transacao,
    delete_transacao,
    get_transacoes_df,
    init_db,
    seed_exemplo_se_vazio,
)

# ----------------------------------------------------------------------------
# Paleta de cores (validada para acessibilidade — ver skill "dataviz")
# ----------------------------------------------------------------------------
COR_SURFACE = "#fcfcfb"
COR_TEXTO_PRIMARIO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_MUTED = "#898781"
COR_GRID = "#e1e0d9"

COR_RECEITA = "#1baf7a"   # aqua (slot 2)
COR_DESPESA = "#e34948"   # red (slot 6)
COR_SALDO = "#2a78d6"     # blue (slot 1) — sequencial/linha principal

PALETA_CATEGORIAS = [
    "#2a78d6",  # blue
    "#1baf7a",  # aqua
    "#eda100",  # yellow
    "#008300",  # green
    "#4a3aa7",  # violet
    "#e34948",  # red
    "#e87ba4",  # magenta
    "#eb6834",  # orange
]

NOMES_MESES = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]

st.set_page_config(
    page_title="Minhas Finanças",
    page_icon="💰",
    layout="wide",
)

try:
    init_db()
    seed_exemplo_se_vazio()
except Exception as erro:
    st.error(
        "Não consegui conectar ao banco de dados na nuvem. Isso normalmente "
        "significa que o secret **SUPABASE_DB_URL** ainda não foi configurado "
        "(ou está incorreto) — veja o README.md, seção 'Configurando o banco "
        "de dados na nuvem', para o passo a passo."
    )
    with st.expander("Detalhes técnicos do erro"):
        st.code(str(erro))
    st.stop()


def formatar_reais(valor: float) -> str:
    texto = f"{valor:,.2f}"
    texto = texto.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


def grafico_layout_base(fig: go.Figure, altura: int = 360) -> go.Figure:
    fig.update_layout(
        height=altura,
        plot_bgcolor=COR_SURFACE,
        paper_bgcolor=COR_SURFACE,
        font=dict(color=COR_TEXTO_PRIMARIO, family="system-ui, -apple-system, 'Segoe UI', sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, linecolor=COR_MUTED, tickfont=dict(color=COR_MUTED))
    fig.update_yaxes(showgrid=True, gridcolor=COR_GRID, zeroline=False, tickfont=dict(color=COR_MUTED))
    return fig


# ----------------------------------------------------------------------------
# Sidebar: navegação e lançamento de transações
# ----------------------------------------------------------------------------
st.sidebar.title("💰 Minhas Finanças")
pagina = st.sidebar.radio("Navegar", ["Dashboard", "Lançar transação", "Todas as transações"])

st.sidebar.divider()
st.sidebar.caption("v0.3 — dados salvos com segurança em um banco na nuvem (Supabase/Postgres).")

df = get_transacoes_df()

# ----------------------------------------------------------------------------
# Página: Lançar transação
# ----------------------------------------------------------------------------
if pagina == "Lançar transação":
    st.header("Lançar nova transação")

    tipo = st.radio("Tipo", ["Despesa", "Receita"], horizontal=True)
    categorias = CATEGORIAS_DESPESA if tipo == "Despesa" else CATEGORIAS_RECEITA

    with st.form("form_transacao", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_transacao = st.date_input("Data", value=date.today())
            categoria = st.selectbox("Categoria", categorias)
        with col2:
            valor = st.number_input("Valor (R$)", min_value=0.0, step=10.0, format="%.2f")
            descricao = st.text_input("Descrição (opcional)")

        enviado = st.form_submit_button("Salvar", use_container_width=True, type="primary")
        if enviado:
            if valor <= 0:
                st.error("Informe um valor maior que zero.")
            else:
                add_transacao(data_transacao, tipo, categoria, descricao, valor)
                st.success(f"{tipo} de {formatar_reais(valor)} em '{categoria}' salva com sucesso!")
                st.rerun()

# ----------------------------------------------------------------------------
# Página: Todas as transações
# ----------------------------------------------------------------------------
elif pagina == "Todas as transações":
    st.header("Todas as transações")

    if df.empty:
        st.info("Nenhuma transação lançada ainda. Vá em 'Lançar transação' para começar.")
    else:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_tipo = st.multiselect("Tipo", ["Receita", "Despesa"], default=["Receita", "Despesa"])
        with col_f2:
            filtro_categoria = st.multiselect(
                "Categoria", sorted(df["categoria"].unique()), default=sorted(df["categoria"].unique())
            )

        df_filtrado = df[df["tipo"].isin(filtro_tipo) & df["categoria"].isin(filtro_categoria)]

        for _, linha in df_filtrado.iterrows():
            c1, c2, c3, c4, c5 = st.columns([1.2, 1, 1.5, 2.5, 0.8])
            c1.write(linha["data"].strftime("%d/%m/%Y"))
            c2.write(linha["tipo"])
            c3.write(linha["categoria"])
            desc = linha["descricao"] if linha["descricao"] else "—"
            c4.write(desc)
            cor = COR_RECEITA if linha["tipo"] == "Receita" else COR_DESPESA
            sinal = "+" if linha["tipo"] == "Receita" else "-"
            c5.markdown(f":{'green' if linha['tipo']=='Receita' else 'red'}[{sinal} {formatar_reais(linha['valor'])}]")
            if st.button("Excluir", key=f"del_{linha['id']}"):
                delete_transacao(int(linha["id"]))
                st.rerun()
        st.divider()

# ----------------------------------------------------------------------------
# Página: Dashboard
# ----------------------------------------------------------------------------
else:
    st.header("Dashboard")

    if df.empty:
        st.info("Nenhuma transação lançada ainda. Vá em 'Lançar transação' para começar.")
    else:
        df["ano"] = df["data"].dt.year
        df["mes"] = df["data"].dt.month

        # --- Filtros de período ------------------------------------------
        anos_disponiveis = sorted(df["ano"].unique(), reverse=True)
        f1, f2 = st.columns(2)
        with f1:
            ano_selecionado = st.selectbox("Ano", anos_disponiveis, index=0)
        with f2:
            mes_selecionado = st.selectbox("Mês", ["Ano inteiro"] + NOMES_MESES, index=0)

        df_ano = df[df["ano"] == ano_selecionado]
        if mes_selecionado == "Ano inteiro":
            df_periodo = df_ano
            rotulo_periodo = f"no ano de {ano_selecionado}"
        else:
            mes_num = NOMES_MESES.index(mes_selecionado) + 1
            df_periodo = df_ano[df_ano["mes"] == mes_num]
            rotulo_periodo = f"em {mes_selecionado}/{ano_selecionado}"

        receitas_periodo = df_periodo.loc[df_periodo["tipo"] == "Receita", "valor"].sum()
        despesas_periodo = df_periodo.loc[df_periodo["tipo"] == "Despesa", "valor"].sum()
        saldo_periodo = receitas_periodo - despesas_periodo

        receitas_total = df.loc[df["tipo"] == "Receita", "valor"].sum()
        despesas_total = df.loc[df["tipo"] == "Despesa", "valor"].sum()
        saldo_total = receitas_total - despesas_total

        # --- KPIs -------------------------------------------------------
        st.caption(f"Mostrando totais {rotulo_periodo}")
        k1, k2, k3, k4 = st.columns(4)
        k1.metric("Receitas do período", formatar_reais(receitas_periodo))
        k2.metric("Despesas do período", formatar_reais(despesas_periodo))
        k3.metric("Saldo do período", formatar_reais(saldo_periodo))
        k4.metric("Saldo acumulado (histórico completo)", formatar_reais(saldo_total))

        st.divider()

        col_a, col_b = st.columns(2)

        # --- Evolução do saldo acumulado (sempre histórico completo) -----
        with col_a:
            st.subheader("Evolução do saldo acumulado")
            st.caption("Histórico completo, não muda com os filtros acima.")
            df_ordenado = df.sort_values("data").copy()
            df_ordenado["valor_assinado"] = df_ordenado.apply(
                lambda r: r["valor"] if r["tipo"] == "Receita" else -r["valor"], axis=1
            )
            df_ordenado["saldo_acumulado"] = df_ordenado["valor_assinado"].cumsum()
            df_diario = df_ordenado.groupby(df_ordenado["data"].dt.date)["saldo_acumulado"].last().reset_index()

            fig_linha = go.Figure()
            fig_linha.add_trace(
                go.Scatter(
                    x=df_diario["data"],
                    y=df_diario["saldo_acumulado"],
                    mode="lines",
                    line=dict(color=COR_SALDO, width=2, shape="spline"),
                    fill="tozeroy",
                    fillcolor="rgba(42, 120, 214, 0.12)",
                    hovertemplate="%{x|%d/%m/%Y}<br>Saldo: R$ %{y:,.2f}<extra></extra>",
                )
            )
            fig_linha = grafico_layout_base(fig_linha)
            st.plotly_chart(fig_linha, use_container_width=True)

        # --- Receita x Despesa por mês (dentro do ano selecionado) -------
        with col_b:
            st.subheader(f"Receita x Despesa por mês — {ano_selecionado}")
            resumo_mensal = df_ano.groupby(["mes", "tipo"])["valor"].sum().reset_index()
            receitas_serie = resumo_mensal[resumo_mensal["tipo"] == "Receita"].set_index("mes")["valor"]
            despesas_serie = resumo_mensal[resumo_mensal["tipo"] == "Despesa"].set_index("mes")["valor"]
            rotulos_meses = NOMES_MESES

            fig_barras = go.Figure()
            fig_barras.add_trace(
                go.Bar(
                    x=rotulos_meses,
                    y=[receitas_serie.get(m, 0) for m in range(1, 13)],
                    name="Receita",
                    marker_color=COR_RECEITA,
                    hovertemplate="%{x}<br>Receita: R$ %{y:,.2f}<extra></extra>",
                )
            )
            fig_barras.add_trace(
                go.Bar(
                    x=rotulos_meses,
                    y=[despesas_serie.get(m, 0) for m in range(1, 13)],
                    name="Despesa",
                    marker_color=COR_DESPESA,
                    hovertemplate="%{x}<br>Despesa: R$ %{y:,.2f}<extra></extra>",
                )
            )
            fig_barras.update_layout(barmode="group")
            fig_barras = grafico_layout_base(fig_barras)
            fig_barras.update_xaxes(type="category")
            st.plotly_chart(fig_barras, use_container_width=True)

        # --- Receita x Despesa por ano (todos os anos) -------------------
        st.subheader("Receita x Despesa por ano")
        resumo_anual = df.groupby(["ano", "tipo"])["valor"].sum().reset_index()
        anos_ordenados = sorted(df["ano"].unique())
        receitas_ano_serie = resumo_anual[resumo_anual["tipo"] == "Receita"].set_index("ano")["valor"]
        despesas_ano_serie = resumo_anual[resumo_anual["tipo"] == "Despesa"].set_index("ano")["valor"]

        fig_anual = go.Figure()
        fig_anual.add_trace(
            go.Bar(
                x=[str(a) for a in anos_ordenados],
                y=[receitas_ano_serie.get(a, 0) for a in anos_ordenados],
                name="Receita",
                marker_color=COR_RECEITA,
                hovertemplate="%{x}<br>Receita: R$ %{y:,.2f}<extra></extra>",
            )
        )
        fig_anual.add_trace(
            go.Bar(
                x=[str(a) for a in anos_ordenados],
                y=[despesas_ano_serie.get(a, 0) for a in anos_ordenados],
                name="Despesa",
                marker_color=COR_DESPESA,
                hovertemplate="%{x}<br>Despesa: R$ %{y:,.2f}<extra></extra>",
            )
        )
        fig_anual.update_layout(barmode="group")
        fig_anual = grafico_layout_base(fig_anual, altura=320)
        fig_anual.update_xaxes(type="category")
        st.plotly_chart(fig_anual, use_container_width=True)

        st.divider()

        # --- Despesas por categoria (respeita o filtro de período) -------
        st.subheader(f"Despesas por categoria ({rotulo_periodo})")
        despesas_categoria = (
            df_periodo[df_periodo["tipo"] == "Despesa"]
            .groupby("categoria")["valor"]
            .sum()
            .sort_values(ascending=True)
        )

        if despesas_categoria.empty:
            st.info("Nenhuma despesa lançada neste período.")
        else:
            fig_cat = go.Figure(
                go.Bar(
                    x=despesas_categoria.values,
                    y=despesas_categoria.index,
                    orientation="h",
                    marker_color=COR_SALDO,
                    text=[formatar_reais(v) for v in despesas_categoria.values],
                    textposition="outside",
                    hovertemplate="%{y}<br>R$ %{x:,.2f}<extra></extra>",
                )
            )
            fig_cat = grafico_layout_base(fig_cat, altura=max(280, 36 * len(despesas_categoria)))
            fig_cat.update_layout(showlegend=False, margin=dict(l=10, r=90, t=40, b=10))
            fig_cat.update_xaxes(range=[0, despesas_categoria.max() * 1.25])
            st.plotly_chart(fig_cat, use_container_width=True)

        # --- Despesas por categoria ao longo dos meses do ano -------------
        despesas_ano = df_ano[df_ano["tipo"] == "Despesa"].copy()
        st.subheader(f"Despesas por categoria ao longo dos meses — {ano_selecionado}")
        if despesas_ano.empty:
            st.info("Nenhuma despesa lançada neste ano.")
        else:
            total_por_categoria = despesas_ano.groupby("categoria")["valor"].sum().sort_values(ascending=False)
            top_categorias = list(total_por_categoria.index[:7])
            despesas_ano["categoria_agrupada"] = despesas_ano["categoria"].where(
                despesas_ano["categoria"].isin(top_categorias), "Outros"
            )
            tem_outros = (despesas_ano["categoria_agrupada"] == "Outros").any()
            ordem_categorias = top_categorias + (["Outros"] if tem_outros else [])

            pivo = despesas_ano.groupby(["mes", "categoria_agrupada"])["valor"].sum().reset_index()

            fig_stack = go.Figure()
            for i, cat in enumerate(ordem_categorias):
                serie = pivo[pivo["categoria_agrupada"] == cat].set_index("mes")["valor"]
                fig_stack.add_trace(
                    go.Bar(
                        x=NOMES_MESES,
                        y=[serie.get(m, 0) for m in range(1, 13)],
                        name=cat,
                        marker_color=PALETA_CATEGORIAS[i % len(PALETA_CATEGORIAS)],
                        hovertemplate=f"%{{x}}<br>{cat}: R$ " + "%{y:,.2f}<extra></extra>",
                    )
                )
            fig_stack.update_layout(barmode="stack")
            fig_stack = grafico_layout_base(fig_stack, altura=420)
            fig_stack.update_xaxes(type="category")
            st.plotly_chart(fig_stack, use_container_width=True)
            if tem_outros:
                n_outros = len(total_por_categoria) - len(top_categorias)
                st.caption(
                    f"As {n_outros} categorias com menor gasto no ano foram agrupadas em 'Outros' "
                    "para manter o gráfico legível."
                )

            # --- Mapa de calor: categoria x mês ---------------------------
            st.subheader(f"Mapa de calor de despesas: categoria x mês — {ano_selecionado}")
            pivo_heat = despesas_ano.groupby(["categoria", "mes"])["valor"].sum().unstack(fill_value=0)
            pivo_heat = pivo_heat.reindex(columns=range(1, 13), fill_value=0)
            ordem_heat = pivo_heat.sum(axis=1).sort_values(ascending=False).index
            pivo_heat = pivo_heat.loc[ordem_heat]

            fig_heat = go.Figure(
                go.Heatmap(
                    z=pivo_heat.values,
                    x=NOMES_MESES,
                    y=list(pivo_heat.index),
                    colorscale=[[0, COR_SURFACE], [1, COR_SALDO]],
                    hovertemplate="%{y} — %{x}<br>R$ %{z:,.2f}<extra></extra>",
                    colorbar=dict(title="R$", tickfont=dict(color=COR_MUTED)),
                )
            )
            fig_heat = grafico_layout_base(fig_heat, altura=max(320, 32 * len(pivo_heat)))
            fig_heat.update_yaxes(showgrid=False, autorange="reversed")
            fig_heat.update_xaxes(type="category")
            st.plotly_chart(fig_heat, use_container_width=True)
