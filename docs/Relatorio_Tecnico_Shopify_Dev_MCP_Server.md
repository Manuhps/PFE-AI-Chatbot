# Relatório Técnico: Implementação do Shopify Dev MCP Server para a Loja-Teste

## 1. Introdução e Objetivos do Projeto

Este relatório técnico descreve a arquitetura e os procedimentos de implementação do servidor Shopify Dev Model Context Protocol (MCP) para a Loja-Teste. No ecossistema de agentes de IA modernos, o protocolo MCP é o padrão-ouro para fornecer contexto em tempo real, permitindo que Large Language Models (LLMs) transcendam os seus dados de treino estáticos.

Para a Loja-Teste, a integração deste servidor permite que o Agente de IA Conversacional aceda dinamicamente a esquemas de API, documentação oficial (`shopify.dev`) e ferramentas de validação. O objetivo é duplo: acelerar o ciclo de desenvolvimento de extensões e garantir que as respostas do assistente sejam tecnicamente rigorosas e livres de alucinações de código.

## 2. Configuração do Ambiente e Requisitos Prévios

Pré-requisitos técnicos:

- Node.js 18+
- Domínio Personalizado (Obrigatório para Customer Accounts MCP)
- Ferramentas de IA Compatíveis: Cursor, Claude Desktop, VSCode (extensão MCP)
- Shopify CLI (última versão)
- Conta de Programador com acesso ao Partner Dashboard

Recomendação: scaffold via `shopify app init`, selecionando o template *React Router*.

## 3. Configuração Detalhada do Servidor Shopify Dev MCP

O servidor `shopify-dev-mcp` deve ser configurado como um servidor local stdio. Executar com:

```bash
npx -y @shopify/dev-mcp@latest
```

VSCode (configuração de utilizador MCP):

1. Abra o VSCode e execute o comando `MCP: Open User Configuration` (Command Palette).
2. No ficheiro de configuração de MCP do utilizador, adicione um bloco `mcpServers` com a entrada abaixo:

```json
{
  "mcpServers": {
    "shopify-dev-mcp": {
      "command": "npx",
      "args": ["-y", "@shopify/dev-mcp@latest"]
    }
  }
}
```

Importante (Windows): se houver erro de conexão, use `command: "cmd"` com `args`: `"/k", "npx", "-y", "@shopify/dev-mcp@latest"`.

Após guardar a configuração, inicie o servidor Dev MCP a partir do VSCode usando `MCP: Start Servers` (Command Palette) ou execute diretamente no terminal:

```bash
npx -y @shopify/dev-mcp@latest
```

## 4. Funcionalidades e Ferramentas de Desenvolvimento (Dev MCP)

Ferramentas expostas e casos de uso:

- `learn_shopify_api`: contextualização e geração de Conversation ID (obrigatória — primeira chamada).
- `search_docs_chunks`: pesquisa vetorial na documentação `shopify.dev`.
- `fetch_full_docs`: recuperação de documentos completos após identificar paths.
- `introspect_graphql_schema`: descoberta dinâmica de esquemas GraphQL.
- `validate_graphql_codeblocks`: valida queries e evita alucinações.
- `validate_theme`: verificação de integridade de temas (requer `LIQUID_VALIDATION_MODE=full`).

Uso recomendado: o agente deve executar `tools/list` para mapear capacidades e parâmetros (ex.: formatos GID `gid://shopify/Product/123`).

## 5. Integração de Comércio com Storefront MCP

Endpoint público de Storefront para a Loja-Teste:

`https://loja-teste-store.myshopify.com/api/mcp`

Notas:

- Storefront MCP não requer autenticação OAuth para operações públicas.
- Cabeçalho obrigatório: `Content-Type: application/json`.

Ferramentas de interação (exemplos):

- `search_shop_catalog`: localizar produtos (o parâmetro `context` deve ser enriquecido com preferências do cliente).
- `update_cart`: adicionar itens; se `cart_id` ausente, cria novo carrinho.
- `search_shop_policies_and_faqs`: fonte de verdade para políticas da loja — usar apenas o payload devolvido.

## 6. Gestão de Dados Autenticados: Customer Accounts MCP

O acesso a dados protegidos exige OAuth 2.0 PKCE.

Descoberta de endpoints:

1. `/.well-known/customer-account-api` → fornece `mcp_api` (endpoint de ferramentas).
2. `/.well-known/openid-configuration` → fornece `authorization_endpoint` e `token_endpoint`.

Guia de implementação resumido:

1. Solicitar Level 2 Protected Customer Data no Partner Dashboard.
2. Configurar `scopes` no ficheiro TOML e `redirect_uris` em `[customer_authentication]`.
3. Implementar fluxo PKCE: gerar `code_challenge`, redirecionar para `authorization_endpoint`, trocar código por `access_token` no `token_endpoint`.
4. Incluir cabeçalho `Authorization: <token>` nas chamadas ao `mcp_api`.

## 7. Validação, Segurança e Boas Práticas

- Ativar `LIQUID_VALIDATION_MODE=full` para validações de tema.
- Tratar erros de validação com mensagens descritivas.
- Manter conformidade PII: apenas manipular PII após aprovação Level 2.
- Implementar backoff para `429` (rate limits).

---