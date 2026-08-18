# Sprint 3 — Contas, categorias e transações

O domínio financeiro segue Route → Service → Repository. Todas as consultas exigem o usuário autenticado e filtram por `user_id`; um UUID de outro usuário nunca concede acesso.

## Regras implementadas

- Contas suportam os tipos corrente, poupança, carteira, digital, dinheiro e investimento.
- Exclusão de conta é lógica para preservar histórico.
- Valores usam `NUMERIC(14,2)` e `Decimal`.
- Somente transações concluídas afetam saldo.
- Receita soma e despesa subtrai.
- Edição reverte o efeito anterior antes de aplicar o novo.
- Exclusão reverte o saldo; duplicação aplica uma nova movimentação.
- Categoria precisa pertencer ao usuário e ter o mesmo tipo da transação.
- A listagem suporta busca, período, conta, categoria, tipo, status, ordenação e paginação.

A migration `20260818_02_finance.py` cria `accounts`, `categories` e `transactions` com índices voltados às consultas multi-tenant.
