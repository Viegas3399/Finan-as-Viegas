# Minhas Finanças — App de Controle Financeiro Pessoal

Um app simples para registrar receitas e despesas e acompanhar tudo em um
dashboard visual e dinâmico: saldo ao longo do tempo, receita x despesa por
mês, e despesas por categoria.

Este projeto foi feito para quem **nunca programou** conseguir ter um app
próprio, publicado online, editável com ajuda de IA (Claude).

## O que já funciona (v0.3)

- Lançar receitas e despesas manualmente (data, categoria, valor, descrição),
  com uma lista ampla de categorias comuns de despesas e receitas.
- Ver, filtrar e excluir transações lançadas.
- Dashboard com filtros de **Ano** e **Mês**, e:
  - Cards de resumo (receitas, despesas e saldo do período selecionado, e saldo
    acumulado total).
  - Gráfico de evolução do saldo acumulado (histórico completo).
  - Gráfico de receita x despesa por mês (dentro do ano selecionado).
  - Gráfico de receita x despesa por ano (todos os anos lançados).
  - Ranking de despesas por categoria no período selecionado.
  - Despesas por categoria ao longo dos meses do ano (gráfico empilhado).
  - Mapa de calor de despesas por categoria x mês.
- Dados salvos num banco de dados **Postgres na nuvem (Supabase)** — não se
  perdem quando o app reinicia.

## Configurando o banco de dados na nuvem

O app precisa de um banco Postgres gratuito no [Supabase](https://supabase.com)
para guardar os lançamentos. Passo a passo:

1. Crie uma conta gratuita em **supabase.com** (pode entrar com GitHub).
2. Clique em **"New project"**. Dê um nome (ex: `financas-viegas`), crie uma
   senha forte para o banco **e guarde essa senha em um lugar seguro**, escolha
   uma região perto de você (ex: São Paulo/`sa-east-1`) e clique em
   **"Create new project"**. Espera 1-2 minutinhos enquanto ele é criado.
3. Já dentro do projeto, vá em **"Project Settings"** (ícone de engrenagem) →
   **"Database"**.
4. Em **"Connection string"**, ative a opção **"Use connection pooling"** e
   deixe o modo em **"Session"** (isso é importante: garante que o app
   consegue conectar de qualquer serviço na nuvem, incluindo o Streamlit
   Cloud). Copie a connection string no formato **URI**.
5. Essa string vem com `[YOUR-PASSWORD]` no meio — substitua pela senha que
   você criou no passo 2.
6. No painel do seu app em **share.streamlit.io**, clique nos três pontinhos
   `⋮` → **"Settings"** → **"Secrets"**, e cole assim (trocando pela sua
   string real):

   ```toml
   SUPABASE_DB_URL = "postgresql://postgres.xxxxxxxx:SUA_SENHA@aws-0-sa-east-1.pooler.supabase.com:5432/postgres"
   ```

7. Salve. O app reinicia sozinho e passa a usar o banco na nuvem — na primeira
   vez, ele cria a tabela automaticamente e adiciona alguns lançamentos de
   exemplo.

Se algo der errado, o app mostra uma mensagem explicando o que verificar, em
vez de travar com um erro técnico.

### Rodando na sua máquina (opcional, para testar mudanças antes de publicar)

Pré-requisito: ter Python instalado (3.9 ou mais novo).

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# edite o .streamlit/secrets.toml com sua connection string do Supabase
streamlit run app.py
```

O app abre automaticamente no navegador, em `http://localhost:8501`. O arquivo
`.streamlit/secrets.toml` nunca é enviado ao GitHub (já está no `.gitignore`),
porque contém a senha do seu banco.

## Próximos passos / ideias futuras

- Orçamento mensal por categoria (com alerta de estouro).
- Metas de economia.
- Múltiplas contas/carteiras.
- Exportar relatórios.
- Autenticação (login), caso vá compartilhar o link publicamente com mais
  pessoas usando o mesmo app.

Este README e o app vão evoluindo conforme o projeto avança.
