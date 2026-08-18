# Sprint 4 — Cartões e faturas

Cartões armazenam somente nome e últimos quatro dígitos; nenhum dado sensível completo é persistido. O limite utilizado corresponde às faturas ainda não pagas.

## Parcelamento e faturas

- Uma compra aceita de 1 a 48 parcelas.
- Compras feitas até o dia de fechamento entram na fatura seguinte; após o fechamento, na subsequente.
- Cada parcela é ligada a uma fatura mensal única por cartão.
- O arredondamento usa `Decimal`; eventuais centavos residuais ficam na última parcela.
- O total da compra precisa caber no limite disponível.
- Faturas passam por aberta, fechada, paga ou atrasada.
- O pagamento exige uma conta do mesmo usuário, saldo suficiente, debita a conta e libera limite.

A migration `20260818_03_credit.py` cria cartões, faturas, compras e parcelas.
