# Sprint 6 — Dashboard e relatórios

O endpoint agregado `/api/v1/reports/dashboard` calcula, para um período: saldo patrimonial, receitas, despesas, economia, taxa de economia, fluxo de caixa, evolução patrimonial, gastos por categoria, contas, cartões, metas, orçamentos, alertas e transações recentes.

Comparativos usam um período anterior com a mesma quantidade de dias. O patrimônio considera saldos das contas, valores reservados em metas e faturas de cartão ainda não pagas. Relatórios aceitam até três anos por consulta e sempre filtram pelo usuário autenticado.

`/api/v1/reports/export.csv` exporta as transações concluídas em UTF-8 com BOM e separador `;`, adequado ao Excel em português.
