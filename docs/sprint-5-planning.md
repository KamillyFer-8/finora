# Sprint 5 — Orçamentos e metas

Orçamentos são definidos por categoria de despesa e período. O valor utilizado é calculado a partir das transações concluídas, garantindo uma única fonte de verdade. A partir de 80% o alerta é amarelo; em 100% ou mais, vermelho.

Contribuições para metas exigem uma conta do mesmo usuário e saldo suficiente. O valor é debitado da conta e somado à meta na mesma transação do banco. Excluir uma contribuição devolve o valor. Metas concluídas atingem 100%, e a previsão usa o ritmo médio observado das contribuições.

A migration `20260818_04_planning.py` cria `budgets`, `goals` e `goal_contributions` com índices multi-tenant.
