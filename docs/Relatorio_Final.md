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

--------------------------------------------------------------------------------

Conclusão

A arquitetura proposta combina scaffold oficial, Dev MCP para validação, Storefront MCP para operações públicas e Customer Accounts MCP para dados autenticados. Seguir as práticas de descoberta de endpoints, validação de operações e gestão de permissões PII é essencial para uma implementação segura e eficaz.
