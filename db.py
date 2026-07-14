"""
Camada de acesso a dados do app de finanças pessoais.

Usa um banco de dados Postgres na nuvem (Supabase) para guardar as
transações, para os dados não se perderem quando o app reiniciar. A conexão
é configurada através de um "secret" chamado SUPABASE_DB_URL — veja o
README.md, seção "Configurando o banco de dados na nuvem", para o passo a
passo de como obter e configurar essa connection string.
"""

from datetime import date

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text

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


@st.cache_resource(show_spinner=False)
def get_engine():
    """Cria (uma única vez por sessão do app) a conexão com o Postgres na nuvem."""
    db_url = st.secrets.get("SUPABASE_DB_URL")
    if not db_url:
        raise RuntimeError(
            "O banco de dados ainda não está configurado. Defina o secret "
            "'SUPABASE_DB_URL' com a connection string do Supabase — veja o "
            "README.md, seção 'Configurando o banco de dados na nuvem'."
        )
    # SQLAlchemy precisa do driver explícito no início da connection string.
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return create_engine(db_url, pool_pre_ping=True)


def init_db():
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS transacoes (
                    id SERIAL PRIMARY KEY,
                    data DATE NOT NULL,
                    tipo TEXT NOT NULL CHECK (tipo IN ('Receita', 'Despesa')),
                    categoria TEXT NOT NULL,
                    descricao TEXT,
                    valor NUMERIC(12, 2) NOT NULL CHECK (valor > 0)
                )
                """
            )
        )


def add_transacao(data_: date, tipo: str, categoria: str, descricao: str, valor: float):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO transacoes (data, tipo, categoria, descricao, valor) "
                "VALUES (:data, :tipo, :categoria, :descricao, :valor)"
            ),
            {"data": data_, "tipo": tipo, "categoria": categoria, "descricao": descricao, "valor": valor},
        )


def delete_transacao(transacao_id: int):
    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transacoes WHERE id = :id"), {"id": transacao_id})


def get_transacoes_df() -> pd.DataFrame:
    engine = get_engine()
    df = pd.read_sql_query(
        "SELECT id, data, tipo, categoria, descricao, valor FROM transacoes ORDER BY data DESC, id DESC",
        engine,
    )
    if not df.empty:
        df["data"] = pd.to_datetime(df["data"])
        df["valor"] = df["valor"].astype(float)
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
