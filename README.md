# Minhas Finanças — App de Controle Financeiro Pessoal

Um app simples para registrar receitas e despesas e acompanhar tudo em um
dashboard visual e dinâmico: saldo ao longo do tempo, receita x despesa por
mês, e despesas por categoria.

Este projeto foi feito para quem **nunca programou** conseguir ter um app
próprio, publicado online, editável com ajuda de IA (Claude).

## O que já funciona (MVP v0.1)

- Lançar receitas e despesas manualmente (data, categoria, valor, descrição).
- Ver, filtrar e excluir transações lançadas.
- Dashboard com:
  - Cards de resumo (receitas, despesas, saldo do mês, saldo total).
  - Gráfico de evolução do saldo acumulado.
  - Gráfico de receita x despesa por mês.
  - Gráfico de despesas por categoria no mês atual.

Os dados ficam salvos em um arquivo local (`financas.db`, SQLite).

## Como rodar na sua máquina

Pré-requisito: ter Python instalado (3.9 ou mais novo).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

O app abre automaticamente no navegador, em `http://localhost:8501`.

## Próximos passos (para publicar online e evoluir)

1. Subir este código para um repositório no GitHub.
2. Publicar no [Streamlit Community Cloud](https://streamlit.io/cloud) (gratuito),
   conectando direto no repositório do GitHub.
3. Trocar o armazenamento local (SQLite) por um banco de dados na nuvem
   (ex: Supabase), para os dados não se perderem quando o app reiniciar.
4. Ideias futuras: orçamento mensal por categoria, metas de economia,
   múltiplas contas/carteiras, exportar relatórios.

Este README e o app vão evoluindo conforme o projeto avança.
