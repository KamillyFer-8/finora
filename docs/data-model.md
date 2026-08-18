# Modelo de dados proposto

Todas as tabelas de domínio possuem `id` UUID, `created_at` e `updated_at`. Valores monetários usam `NUMERIC(14,2)`, nunca ponto flutuante. Datas financeiras usam `date`; eventos e auditoria usam timestamps UTC.

| Entidade | Campos centrais | Relações e restrições |
|---|---|---|
| users | email, password_hash, name, locale, timezone, is_active | email único |
| accounts | user_id, name, institution, type, balance, currency, is_active | pertence ao usuário |
| categories | user_id opcional, name, type, color, icon | categorias do sistema ou do usuário |
| transactions | user_id, account_id, category_id, card_id, invoice_id, type, amount, date, status, description, installment data | isolamento por user_id; vínculos coerentes com o tipo |
| cards | user_id, account_id, name, last_four, limit, closing_day, due_day, is_active | pertence ao usuário; últimos 4 sem dados sensíveis |
| invoices | user_id, card_id, period_start, period_end, due_date, total, status | único por cartão e período |
| budgets | user_id, category_id, period_start, period_end, limit_amount | único por categoria/período/usuário |
| goals | user_id, name, target_amount, current_amount, deadline, status | current_amount derivável das contribuições |
| goal_contributions | goal_id, user_id, amount, contributed_at, account_id | pertence à mesma pessoa da meta |
| attachments | user_id, transaction_id, storage_key, url, mime_type, size | metadados; arquivo no armazenamento local |
| recurrences | user_id, transaction template, frequency, interval, next_run_at, end_date | geração idempotente |
| refresh_tokens | user_id, token_hash, expires_at, revoked_at, family_id | token armazenado apenas como hash |

## Integridade

- Índices começam por `user_id` nas consultas multi-tenant.
- Repositórios sempre filtram pelo usuário autenticado; IDs externos nunca bastam sozinhos.
- Exclusões financeiras devem preferir arquivamento ou soft delete quando a rastreabilidade for necessária.
- Faturas e parcelamentos são alterados em transações atômicas no banco.
- Saldos e totais apresentados podem ser agregados, mas sua fonte de verdade são lançamentos válidos e regras do backend.

As migrations concretas entram junto dos módulos de domínio nas sprints correspondentes, evitando criar agora tabelas sem regras e contratos consolidados.
