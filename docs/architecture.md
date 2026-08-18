# Arquitetura da solução

## Visão geral

O Finora usa um monorepo simples, sem ferramenta adicional de orquestração nesta fase. O frontend e o backend têm ciclos de build independentes e são reunidos pelo Docker Compose.

```text
Browser
  -> Next.js (interface, estado de UI e cache de dados)
  -> REST /api/v1 via Axios
  -> FastAPI (rotas e validação HTTP)
  -> Service (regras financeiras e autorização)
  -> Repository (persistência)
  -> PostgreSQL
```

Anexos seguem o fluxo `Next.js -> FastAPI -> StorageService`. Metadados ficam no PostgreSQL e os arquivos são gravados em um volume local no ambiente de desenvolvimento. A regra de negócio depende apenas da abstração de armazenamento, permitindo trocar o adaptador no futuro.

## Backend

- `api/v1`: roteamento e contratos HTTP; não contém regra financeira.
- `services`: casos de uso, autorização e transações de negócio.
- `repositories`: consultas e persistência SQLAlchemy.
- `models`: mapeamento ORM.
- `schemas`: entrada e saída Pydantic.
- `core`: configuração, segurança futura, erros e logging.
- `db`: engine, sessões e base declarativa.

As regras críticas (parcelamento, fechamento de faturas, limites, orçamento e isolamento por usuário) pertencem ao service/backend e serão cobertas por Pytest.

## Redux Toolkit x TanStack Query

TanStack Query gerencia estado vindo do servidor: contas, transações, cartões, faturas, orçamentos, metas e relatórios. Ele cuida de cache, invalidação, loading, erro e refetch.

Redux Toolkit guarda apenas estado global da interface: período selecionado, filtros compartilhados, tema, notificações e preferências. Dados da API não devem ser duplicados no Redux. Estados efêmeros de um componente permanecem em `useState` ou `useReducer`.

## Comunicação Next.js e FastAPI

O frontend usa uma instância Axios configurada por `NEXT_PUBLIC_API_URL`. Recursos chamarão endpoints REST versionados em `/api/v1`. O backend devolve JSON com schemas estáveis e erros centralizados. Na Sprint 2, access tokens curtos serão enviados no cabeçalho `Authorization`; refresh tokens serão tratados de forma segura, preferencialmente com cookie HttpOnly. Chamadas públicas ou adequadas à renderização inicial poderão partir de Server Components; interações e cache reativo usam TanStack Query no cliente.

## Decisões da Sprint 1

- App Router e Server Components por padrão; `use client` somente nos providers e componentes interativos.
- Runtime Node.js padrão e saída `standalone` para a imagem Docker.
- Tailwind como sistema principal, com tokens CSS semânticos para preservar a identidade.
- API desacoplada e versionada desde o início.
- Nenhuma regra financeira implementada exclusivamente no frontend.
