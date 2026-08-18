# Sprint 7 — Qualidade e produção

## Entregas

- anexos PDF, JPEG e PNG vinculáveis a transações, com limite de 10 MB e isolamento por usuário;
- armazenamento local persistente atrás do contrato `StorageService`, segregado por usuário;
- tratamento interno de erros com Error Boundaries, respostas padronizadas e logs estruturados;
- logs JSON da API com identificador de requisição, status e duração;
- telas de erro globais e locais com recuperação;
- foco visível, atalho para conteúdo e respeito a movimento reduzido;
- testes Playwright em desktop e mobile, incluindo auditoria automatizada com axe;
- pipeline CI completo para lint, tipos, testes, build e E2E.

## Critérios operacionais

Defina `UPLOAD_DIR` para escolher o diretório persistente de anexos. No Docker Compose, esse
diretório usa um volume nomeado. Os arquivos são entregues apenas por rota autenticada da API.

## Checklist de release

- aplicar todas as migrações Alembic;
- configurar CORS somente com os domínios de produção;
- trocar `SECRET_KEY` por um segredo forte gerenciado pela plataforma;
- validar backup e retenção do volume de anexos;
- executar o pipeline CI e um smoke test após o deploy.

## Entregas finais

- busca global, notificações internas, perfil, ajuda e configurações;
- edição, filtros avançados, recorrências, cartão/parcelamento e comprovante no fluxo de transações;
- componentes reutilizáveis de seleção, badge, progresso, skeleton, estado vazio e erro;
- orçamento automatizado de até 3 MB para JavaScript estático após o build;
- workflow de publicação do frontend na Vercel, acionado na `main` ou manualmente, condicionado aos secrets do projeto.
