"""
Camada de acesso a dados do app de finanças pessoais.

Usa SQLite (um arquivo local, `financas.db`) para guardar as transações.
Isso é ótimo para testar o app agora; quando formos publicar online de
verdade, vamos trocar isso por um banco de dados na nuvem (ex: Supabase)
para os dados não se perderem a cada atualização do app. Essa troca fica
para uma etapa futura — o restante do código (formulários, dashboard)
não muda.
"""

import sqlite3
from contextlib import contextmanager
from datetime import date

import pandas as pd

DB_PATH = "financas.db"

CATEGORIAS_DESPESA = [
    "Moradia",
    "Contas e Serviços",
    "Alimentação",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer e Entretenimento",
    "Vestuário e Calçados",
    "Cuidados Pessoais",
    "Assinaturas e Streaming",
    "Viagens",
    "Pets",
    "Presentes e Doações",
    "Dívidas e Empréstimos",
    "Impostos e Taxas",
    "Imprevistos",
    "Compras",
    "Outros",
]

CATEGORIAS_RECEITA = [
    "Salário",
    "Freelance / Renda Extra",
    "Investimentos",
    "Vendas",
    "Reembolso",
    "Presente",
    "Outros",
]


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS transacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
                categoria TEXT NOT NULL,
                descricao TEXT,
                valor REAL NOT NULL CHECK (valor > 0)
            )
            """
        )
        conn.commit()


def add_transacao(data_: date, tipo: str, categoria: str, descricao: str, valor: float):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO transacoes (data, tipo, categoria, descricao, valor) VALUES (?, ?, ?, ?, ?)",
            (data_.isoformat(), tipo, categoria, descricao, valor),
        )
        conn.commit()


def delete_transacao(transacao_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM transacoes WHERE id = ?", (transacao_id,))
        conn.commit()


def get_transacoes_df() -> pd.DataFrame:
    with get_conn() as conn:
        df = pd.read_sql_query(
            "SELECT id, data, tipo, categoria, descricao, valor FROM transacoes ORDER BY data DESC, id DESC",
            conn,
        )
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
    return df


def _mes_atras(hoje: date, n: int) -> date:
    """Retorna o dia 1 do mês `n` meses atrás de `hoje` (sem depender de libs extras)."""
    mes = hoje.month - n
    ano = hoje.year
    while mes <= 0:
        mes += 12
        ano -= 1
    return date(ano, mes, 1)


def seed_exemplo_se_vazio():
    """Adiciona alguns lançamentos de exemplo (3 meses) na primeira execução,
    só para o dashboard não aparecer vazio antes do usuário lançar nada."""
    df = get_transacoes_df()
    if not df.empty:
        return

    hoje = date.today()
    m0 = _mes_atras(hoje, 0)  # mês atual
    m1 = _mes_atras(hoje, 1)
    m2 = _mes_atras(hoje, 2)

    exemplos = []
    for m in (m2, m1, m0):
        exemplos += [
            (m.replace(day=1), "Receita", "Salário", "Salário do mês", 5000.0),
            (m.replace(day=3), "Despesa", "Moradia", "Aluguel", 1500.0),
            (m.replace(day=4), "Despesa", "Contas e Serviços", "Água, luz e internet", 320.0),
            (m.replace(day=6), "Despesa", "Alimentação", "Supermercado", 620.0),
            (m.replace(day=8), "Despesa", "Transporte", "Combustível e app de transporte", 260.0),
            (m.replace(day=10), "Despesa", "Saúde", "Plano de saúde", 350.0),
            (m.replace(day=12), "Despesa", "Lazer e Entretenimento", "Cinema e restaurante", 150.0),
            (m.replace(day=14), "Despesa", "Assinaturas e Streaming", "Streamings", 60.0),
            (m.replace(day=18), "Despesa", "Vestuário e Calçados", "Roupas", 120.0),
        ]
    # alguns lançamentos só em meses específicos, pra dar variação real
    exemplos += [
        (m1.replace(day=20), "Despesa", "Viagens", "Passagem de ônibus", 300.0),
        (m0.replace(day=15), "Despesa", "Cuidados Pessoais", "Salão de beleza", 90.0),
        (m0.replace(day=20), "Receita", "Freelance / Renda Extra", "Projeto extra", 800.0),
    ]

    for data_, tipo, categoria, descricao, valor in exemplos:
        add_transacao(data_, tipo, categoria, descricao, valor)
