Relatório de Arquitetura Técnica: AI Chatbot Loja-Teste

Este relatório organiza a arquitetura técnica e os protocolos de integração para o chatbot de IA da Loja-Teste no ecossistema Shopify. A solução é baseada no Model Context Protocol (MCP) e foca em desenvolvimento seguro, validação técnica e operações de comércio.

--------------------------------------------------------------------------------

Sumário executivo

- Objetivo: construir um agente conversacional capaz de operar com segurança no Shopify, fornecendo respostas fundamentadas, ações de carrinho via Storefront MCP e operações administrativas validadas pelo Dev MCP.
- Benefícios-chave: redução do abandono de carrinho, automação de suporte ao cliente e desenvolvimento com menor risco de alucinações de código.

--------------------------------------------------------------------------------

1. Scaffold da aplicação (fundação)

- Processo de inicialização: `shopify app init` → selecionar template "Build a React Router app" → usar `shopify app dev` para servidor local.
- Infraestrutura local gerada: túnel HTTPS (Cloudflare) e persistência local (Prisma SQLite) para estado e dados de desenvolvimento.

--------------------------------------------------------------------------------

2. Dev MCP — ambiente de desenvolvimento e validação

- O Shopify Dev MCP server conecta assistentes de IA às ferramentas oficiais da Shopify para introspecção e validação.
- Ferramentas essenciais:
  - `learn_shopify_api` (obrigatório como primeiro passo)
  - `introspect_graphql_schema`
  - `validate_graphql_codeblocks`
  - `validate_component_codeblocks`
  - `validate_theme` (recomenda-se `LIQUID_VALIDATION_MODE=full` para validação de temas)

--------------------------------------------------------------------------------

3. Storefront MCP — capacidades de front‑of‑store

- Endpoint: `https://{shop}.myshopify.com/api/mcp` (não requer autenticação para operações públicas).
- Ferramentas e uso principal:
  - `search_shop_catalog` — pesquisa produtos (usar URLs retornadas para links);
  - `search_shop_policies_and_faqs` — respostas baseadas na documentação da loja;
  - `get_cart` / `update_cart` — criar/atualizar carrinhos; `update_cart` cria novo carrinho se `cart_id` ausente.

Exemplo de requisição JSON-RPC (search_shop_catalog):

```
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "search_shop_catalog",
    "arguments": {
      "query": "coffee beans",
      "context": "Customer looking for dark roast"
    }
  }
}
```

--------------------------------------------------------------------------------

4. Customer Accounts MCP — dados autenticados e PII

- Uso: histórico de encomendas, dados de cliente e ações autenticadas.
- Requisitos: domínio personalizado, aprovação de acesso a PII (Level 2) via Partner Dashboard e fluxo OAuth 2.0 com PKCE.

Descoberta de endpoints:
1. `/.well-known/customer-account-api` → obtém `mcp_api`.
2. `/.well-known/openid-configuration` → obtém `authorization_endpoint` e `token_endpoint`.

Ao solicitar autorização, usar `scope=customer-account-mcp-api:full` conforme as regras do Shopify.

--------------------------------------------------------------------------------

5. Segurança, autenticação e gestão de segredos

- Armazenar `SHOPIFY_ADMIN_TOKEN` e outras chaves no servidor (env vars, secret store); nunca expor ao cliente.
- Para Customer Accounts, implementar PKCE e seguir políticas de acesso a PII.

--------------------------------------------------------------------------------

6. Protocolos de interface e validação (checklist)

- Identificadores: usar formato `gid://shopify/<Type>/<id>`.
- Datas: usar ISO 8601.
- Gestão de carrinho: `quantity: 0` para remover itens via `update_cart`.
- Monetário: incluir códigos de moeda (ex: EUR, BRL).
- Erros e rate limits: mensagens descritivas por campo; retornar "Unable to process the request, try again" para falhas genéricas; implementar backoff para `429`.

--------------------------------------------------------------------------------

7. Impacto e benefícios para a organização

- Redução do abandono de carrinho: chatbot atuando como "Personal Shopper" pode recuperar uma percentagem significativa de carrinhos abandonados e acelerar conversões.
- Redução de custos de suporte: atender até 93% das questões comuns automaticamente para clientes autenticados (quando habilitado).
- Desenvolvimento seguro: uso obrigatório de `learn_shopify_api` e ferramentas de validação do Dev MCP reduz o risco de alucinações de código.


Conclusão

A arquitetura proposta combina scaffold oficial, Dev MCP para validação, Storefront MCP para operações públicas e Customer Accounts MCP para dados autenticados. Seguir as práticas de descoberta de endpoints, validação de operações e gestão de permissões PII é essencial para uma implementação segura e eficaz.

8. Implementação Prática do Chatbot

- Objetivo: fornecer um caminho mínimo viável (MVP) para integrar um chatbot conversacional na Loja-Teste usando MCP para buscas de catálogo, gestão de carrinho e dados autenticados.

- Arquitetura recomendada: Frontend (React) <-> Backend proxy (FastAPI) <-> Storefront MCP (https://{shop}.myshopify.com/api/mcp)  |  Dev MCP usado para validação durante desenvolvimento.

- Endpoints mínimos do backend (exemplos):
  - `POST /api/search` — recebe `{query, context}` do frontend, faz JSON-RPC `search_shop_catalog` ao MCP, parseia `result.content[0].text` se necessário e retorna JSON estruturado.
  - `GET /api/cart/{cart_id}` — encaminha `get_cart` e retorna estado normalizado.
  - `POST /api/cart` — recebe `{cart_id?, add_items?, remove_items?}` e chama `update_cart`, retorna `cart_id` e `checkout_url`.
  - `POST /api/policies` — encaminha `search_shop_policies_and_faqs` e retorna respostas.
  - `GET /api/auth/callback` — endpoint de callback PKCE (troca `code` por token e guarda em servidor seguro).

- Dependências backend sugeridas: `fastapi`, `httpx`, `uvicorn`, `python-dotenv`.

- Exemplo de corpo JSON-RPC (proxy enviaria):

```
{
  "jsonrpc":"2.0",
  "method":"tools/call",
  "id":"tx-001",
  "params":{
    "name":"search_shop_catalog",
    "arguments":{"query":"sapatilhas de corrida","context":"cliente procura sapatilhas de corrida"}
  }
}
```

- Segurança e configuração de ambiente:
  - Variáveis sensíveis (ex.: `SHOP_DOMAIN`, `ADMIN_TOKEN`) só no servidor; nunca expor no frontend.
  - Para Customer Accounts: implementar PKCE no fluxo OAuth e armazenar tokens em secret store.

- Frontend (mínimo): componente React que chama `/api/search`, renderiza lista de produtos, permite adicionar ao carrinho via chamadas a `/api/cart` e apresenta `checkout_url` retornado.

- Testes e ferramentas de verificação:
  - Curl/PowerShell exemplos para replicar chamadas JSON-RPC ao MCP (usar o preview domain do `shopify app dev`).
  - Scripts de integração para validar parsing de `result.content[0].text` e checar `checkout_url` retornado.

- Comandos de execução rápida (exemplo):

```
# Backend (Python)
python -m venv .venv
.venv\Scripts\activate
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload --port 8000

# Frontend (React)
# criar com `npx create-react-app frontend` (uma vez)
cd frontend
npm install
npm start
```

- Observabilidade e produção:
  - Adicionar caching (TTL curtos) para resultados de `search_shop_catalog` e rate limiting no proxy.
  - Registar métricas básicas (requests, latência, erros) e logs estruturados para troubleshooting.

- Checklist de entrega:
  1. Proxy implementado e testado localmente com o preview domain.
  2. Fluxo PKCE testado e tokens armazenados com segurança.
  3. Frontend básico que realiza buscas e inicia checkout via `checkout_url`.
  4. Documentação com comandos de teste e exemplos de payload (incluir em `backend/README.md` e `frontend/README.md`).

9. Fluxo de trabalho AI Chatbot

Descrição: o seguinte é um guia operativo preciso que descreve como o chatbot deve funcionar em produção, incluindo decisões, chamadas e tratamento de estado.

- 2) Classificação de intenção e extracção de entidades
  - Executar um intent classifier local ou serviço externo (intents: `search`, `add_to_cart`, `view_cart`, `policy`, `auth`, `fallback`).
  - Extrair slots: `query`, `quantity`, `variant_id`, filtros (preço, tamanho) e normalizar valores.

- 3) Enriquecimento do contexto
  - Anexar informação contextual: histórico curto da conversa, preferências de idioma, localização e estado do carrinho.
  - Resolver ambiguidades (ex.: perguntar tamanho se não fornecido).

- 4) Planeamento e mapeamento para ferramenta MCP
  - Mapear intenção para ferramenta MCP apropriada: `search_shop_catalog`, `update_cart`, `get_cart`, `search_shop_policies_and_faqs`.
  - Decidir chamada via proxy REST interno (`/api/search`, `/api/cart`) que traduz para JSON‑RPC.

- 5) Chamada ao proxy e envio JSON‑RPC
  - Frontend faz REST ao proxy (ex.: `POST /api/search`), não chama MCP diretamente.
  - Proxy constrói JSON‑RPC conforme o padrão e faz `POST` a `https://{shop}.myshopify.com/api/mcp`.
  - Configurar timeouts (~5s) e 1–2 retries com backoff exponencial.

- 6) Normalização do resultado
  - Proxy parseia `result.content[0].text` (quando presente) e valida o JSON.
  - Normalizar campos para o frontend: `product_id`, `title`, `description`, `price` (number + currency), `image_url`, `variants`, `checkout_url`.

- 7) Resposta ao utilizador e actualização do estado
  - Gerar resposta conversacional curta + blocos de produto (cartões) com CTAs (`Adicionar`, `Ver checkout`).
  - Se `update_cart` criou/alterou `cart_id`, persistir no estado da sessão.

- 8) Persistência e observabilidade
  - Guardar `cart_id`, última query e timestamps (Redis/SQLite). Logar eventos e métricas (latência, erros, hits de cache).


- Sequência técnica rápida (exemplo)
  1. UI -> `POST /api/search` {"query":"tênis de corrida","session_id":"s-123"}
  2. Proxy -> JSON‑RPC `search_shop_catalog` -> MCP -> retorna payload
  3. Proxy parseia e devolve lista de produtos ao UI
  4. UI -> `POST /api/cart` {"add_items":[{"merchandise_id":"gid://shopify/ProductVariant/111","quantity":1}],"session_id":"s-123"}
  5. Proxy -> JSON‑RPC `update_cart` -> MCP -> retorna `cart_id` e `checkout_url`
  6. Proxy persiste `cart_id` e retorna `checkout_url` ao UI

