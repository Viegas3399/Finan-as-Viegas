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
    "Alimentação",
    "Moradia",
    "Transporte",
    "Saúde",
    "Educação",
    "Lazer",
    "Compras",
    "Contas e Serviços",
    "Outros",
]

CATEGORIAS_RECEITA = [
    "Salário",
    "Freelance",
    "Investimentos",
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


def seed_exemplo_se_vazio():
    """Adiciona alguns lançamentos de exemplo na primeira execução,
    só para o dashboard não aparecer vazio antes do usuário lançar nada."""
    df = get_transacoes_df()
    if not df.empty:
        return
    hoje = date.today()
    exemplos = [
        (hoje.replace(day=1), "Receita", "Salário", "Salário do mês", 5000.0),
        (hoje.replace(day=2), "Despesa", "Moradia", "Aluguel", 1500.0),
        (hoje.replace(day=3), "Despesa", "Alimentação", "Supermercado", 620.0),
        (hoje.replace(day=5), "Despesa", "Transporte", "Combustível", 250.0),
        (hoje.replace(day=7), "Despesa", "Lazer", "Cinema", 80.0),
        (hoje.replace(day=10), "Despesa", "Contas e Serviços", "Internet e celular", 180.0),
    ]
    for data_, tipo, categoria, descricao, valor in exemplos:
        add_transacao(data_, tipo, categoria, descricao, valor)
