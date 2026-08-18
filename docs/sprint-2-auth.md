# Sprint 2 — Autenticação

O backend implementa cadastro, login, consulta do usuário atual, rotação de refresh token, logout, solicitação e redefinição de senha. Senhas usam Argon2; refresh tokens e tokens de recuperação são persistidos somente como SHA-256. Access e refresh tokens são entregues em cookies HttpOnly com `SameSite=Lax`.

Em desenvolvimento, o endpoint de recuperação devolve o token para permitir testes locais. Em produção ele sempre retorna apenas a mensagem genérica e a futura integração de e-mail deverá entregar o link ao usuário.

Antes de produção, defina `JWT_SECRET_KEY` com segredo aleatório, habilite `COOKIE_SECURE=true`, use HTTPS e configure origens CORS exatas. A migration `20260818_01_auth.py` cria as três tabelas da sprint.
