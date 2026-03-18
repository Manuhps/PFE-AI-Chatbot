# Relatório Técnico: Scaffolding e Infraestrutura de Apps Shopify para Agentes de IA

## 1. Introdução e Contexto do Projeto

Este relatório define os protocolos de infraestrutura e a configuração técnica do scaffold de uma aplicação Shopify para a loja "Loja-Teste". O objetivo central é estabelecer uma fundação de alto desempenho para um Agente de IA Conversacional Autónomo, utilizando o Model Context Protocol (MCP) para consumo síncrono de dados de catálogo e clientes.

## 2. Requisitos Prévios do Sistema

Obrigatório para estabilidade do ambiente de desenvolvimento:

- Node.js: 18.0.0 ou superior.
- Shopify CLI: versão mais recente instalada globalmente.
- Navegadores: Chrome ou Firefox atualizados.
- Permissões: utilizador com privilégios de desenvolvimento e uma dev store ativa.

> Aviso de Propriedade: para operar com a Shopify CLI, deve ser o proprietário da dev store ou conta de staff verificada.

## 3. Scaffolding da Aplicação via Shopify CLI

Processo de inicialização via `shopify app init` — gera o código base e instala dependências.

### Procedimento de Inicialização (Terminal)

```bash
# Inicializar o scaffold da aplicação
shopify app init

# Selecionar "Build a React Router app" nos prompts
cd loja-teste-ai-agent
```

## 4. Configuração do Ambiente de Desenvolvimento Local

O comando `shopify app dev` orquestra a infraestrutura local:

1. Autenticação: login para conta de parceiro/lojista.
2. Sincronização: regista a app no Dev Dashboard.
3. Persistência: instala e configura Prisma SQLite.
4. Túnel HTTPS: cria túnel Cloudflare para exposição segura.

### Instalação e Teste

- Com o servidor ativo, prima `p` para abrir o preview.
- Instale a app na dev store seleccionada.
- Use a ferramenta "Generate a product" para popular dados de teste.

## 5. Integração de Servidores MCP

A arquitetura é segmentada em três servidores MCP para separação de contexto e segurança:

### 5.1 Shopify Dev MCP Server

- Comando: `npx -y @shopify/dev-mcp@latest`
- Utilidade: acesso à documentação técnica e esquemas GraphQL para validação.

### 5.2 Storefront MCP Server

- Endpoint: `https://{shop}.myshopify.com/api/mcp`
- Ações: pesquisa de catálogo, gestão de carrinho e FAQs públicas.

### 5.3 Customer Accounts MCP Server

- Requisitos: domínio personalizado e aprovação PII.
- Descoberta do endpoint via `/.well-known/customer-account-api`.

Exemplo de descoberta:

```js
const discoveryResponse = await fetch(`https://${shopDomain}/.well-known/customer-account-api`);
const apiConfig = await discoveryResponse.json();
const mcpEndpoint = apiConfig.mcp_api; // https://{shopDomain}/customer/api/mcp
```

## 6. Arquitetura de Autenticação e Dados Protegidos

O acesso ao Customer Accounts MCP exige OAuth 2.0 com PKCE (S256).

### Matriz de Configuração

- Escopos (TOML): e.g., `scopes = "customer_read_orders,..."`
- Permissões PII: Nível 2 para dados sensíveis.
- Fluxo PKCE: `S256` com `code_challenge`.

### Construção do URL de Autorização

```js
const oauthDiscovery = await fetch(`https://${shopDomain}/.well-known/openid-configuration`);
const oauthConfig = await oauthDiscovery.json();

const params = new URLSearchParams({
  client_id: 'YOUR_APP_ID',
  redirect_uri: 'YOUR_REDIRECT_URI',
  response_type: 'code',
  scope: 'customer-account-mcp-api:full',
  state: 'RANDOM_HEX',
  code_challenge: 'PKCE_CHALLENGE_GENERATED',
  code_challenge_method: 'S256'
});

const authUrl = `${oauthConfig.authorization_endpoint}?${params}`;
```

> Nota: após configurar a autenticação, reinicie o servidor com `shopify app dev --use-localhost`.


