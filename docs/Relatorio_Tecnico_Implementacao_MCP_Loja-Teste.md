# Relatório Técnico: Implementação de Servidores MCP na Infraestrutura da Loja-Teste

## 1. Introdução ao Ecossistema MCP para a Loja-Teste

Este relatório detalha a implementação do Model Context Protocol (MCP) na infraestrutura da Loja-Teste. O MCP é um protocolo de arquitetura aberto que estabelece uma interface padronizada entre assistentes de IA e os recursos de dados comerciais da Shopify.

O objetivo estratégico desta implementação é permitir que agentes inteligentes consumam documentação técnica, consultem esquemas de API em tempo real e executem operações comerciais autenticadas. Ao adotar o MCP, a Loja-Teste evolui de modelos de linguagem genéricos para agentes contextuais capazes de agir diretamente sobre o catálogo, carrinhos e dados de clientes, garantindo uma experiência de compra conversacional precisa e segura.

## 2. Preparação da Infraestrutura: Estruturação da Aplicação (Scaffold an app)

A base para qualquer integração avançada na Shopify exige a inicialização de uma aplicação via Shopify CLI. Este processo configura o ambiente necessário para hospedar os servidores MCP e gerir a autenticação.

### Processo de Inicialização

1. Criação da App: Execute o comando `shopify app init`. Ao ser solicitado, defina o nome da aplicação e selecione o template *Build a React Router app*.
2. Início do Servidor Local: Navegue até o diretório e execute `shopify app dev`.

### Tarefas Automáticas do `shopify app dev`

O comando `dev` automatiza processos complexos de infraestrutura:

- Túnel Cloudflare: cria um túnel HTTPS seguro entre a máquina local e a web para webhooks e comunicação com a Shopify.
- Base de Dados SQLite (Prisma): inicializa o armazenamento local para persistência de dados e sessões.
- Conexão ao Partner Dashboard: regista automaticamente a app no painel de parceiros e sincroniza o ficheiro `.toml`.

> Requisito de Segurança: uso de uma *dev store* é obrigatório para testes antes do deploy em produção.

## 3. Otimização do Desenvolvimento: Shopify Dev MCP Server

O Shopify Dev MCP Server integra o assistente de IA no fluxo técnico, fornecendo acesso à documentação oficial e validação de código.

### Configuração e Requisitos de Sistema

- Ambiente: Node.js 18 ou superior.
- IDEs Suportadas: Cursor, Claude Code, VSCode (via extensão MCP), Gemini CLI.

### Blocos de Configuração (exemplo)

Configuração Padrão:

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

Configuração Alternativa (Windows):

```json
{
  "mcpServers": {
    "shopify-dev-mcp": {
      "command": "cmd",
      "args": ["/k", "npx", "-y", "@shopify/dev-mcp@latest"]
    }
  }
}
```

### Ferramentas e Regras de Ouro

- `learn_shopify_api` (Prioridade Máxima): invocar sempre em primeiro lugar — fornece instruções atualizadas e gera um Conversation ID.
- `search_docs_chunks`: pesquisa granular na documentação `shopify.dev`.
- `introspect_graphql_schema`: explora mutações e queries disponíveis.
- Validação de Código: `validate_theme` (requer `LIQUID_VALIDATION_MODE=full`) e `validate_theme_codeblocks` (uso limitado).

## 4. Experiência de Compra Conversacional: Storefront MCP Server

Este servidor conecta a IA ao catálogo em tempo real. Corre no contexto da loja e permite operações de carrinho sem autenticação obrigatória (pública).

- Endpoint previsto: `https://loja-teste-store.myshopify.com/api/mcp`
- Protocolo: JSON-RPC 2.0

Exemplo de chamada JSON-RPC:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "id": 1,
  "params": {
    "name": "search_shop_catalog",
    "arguments": {
      "query": "sapatilhas de corrida",
      "context": "Cliente procura alta durabilidade para maratonas"
    }
  }
}
```

### Definições de Ferramentas
### "Exemplos de paths"
- `search_shop_catalog`: localiza produtos. Parâmetros obrigatórios: `query` e `context`.
- `get_cart`: recupera estado do carrinho via `cart_id` (GID).
- `update_cart`: adiciona/remove itens; se `cart_id` omitido, inicia novo carrinho.

## 5. Gestão Avançada e Segurança: Customer Accounts MCP Server

Requisitos de conformidade:

1. Domínio personalizado: obrigatório.
2. Acesso PII Nível 2: solicitar no Partner Dashboard.
3. Escopos (TOML): definir (ex: `customer_read_orders`) conforme pedido de autorização.

### Fluxo de Autenticação (OAuth 2.0 PKCE)

Descoberta de endpoints via `.well-known`:

```js
const params = new URLSearchParams({
  client_id: 'LOJA_TESTE_APP_ID',
  redirect_uri: 'https://loja-teste-app.com/callback',
  response_type: 'code',
  scope: 'customer-account-mcp-api:full',
  code_challenge: 'PKCE_CHALLENGE',
  code_challenge_method: 'S256'
});
```

Ao chamar o MCP após obter o token, incluir `Authorization: YOUR_ACCESS_TOKEN`.

### Padrões de Dados

- Global IDs (GID): obrigatório (`gid://shopify/Order/123456789`).
- Datas: formato ISO 8601 (`2023-10-27T10:00:00Z`).

