# Deploy

## Backend

Execute a imagem descrita em `backend/Dockerfile`, conectada a PostgreSQL. Antes de liberar
tráfego, rode `alembic upgrade head`. Configure as variáveis de autenticação, banco e CORS
conforme `.env.example`. Monte um volume persistente no diretório definido por `UPLOAD_DIR`.

## Frontend

Construa `frontend/Dockerfile` com `NEXT_PUBLIC_API_URL` apontando para a API pública e sirva
a aplicação na porta 3000.

## Saúde e rollback

Use `/api/v1/health` como health check. Faça deploy imutável por imagem, mantenha a versão
anterior disponível para rollback, controle o banco pelo Alembic e execute um smoke test após
a publicação. Trate migrações destrutivas em duas etapas para preservar compatibilidade.

O workflow `.github/workflows/deploy.yml` publica o frontend na Vercel quando os secrets
`VERCEL_TOKEN`, `VERCEL_ORG_ID` e `VERCEL_PROJECT_ID` estiverem configurados no GitHub.
O backend e o PostgreSQL continuam preparados como imagens Docker portáveis; a escolha do
provedor de hospedagem do backend fica desacoplada da aplicação.
