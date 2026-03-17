# Relatório Técnico: Integração do Servidor Storefront MCP no Agente Xtreme

## 1. Introdução e Visão Geral do Storefront MCP

O servidor Storefront MCP (Model Context Protocol) constitui o stateless JSON-RPC bridge entre agentes de IA e o ecossistema de dados comerciais da Shopify. Para o Agente Xtreme, permite interação direta com catálogo e lógica transacional sem interface gráfica tradicional.

Finalidade: habilitar navegação assistida, gestão dinâmica de carrinhos e resolução de dúvidas sobre políticas, focado em dados públicos de front-of-house.

## 2. Arquitetura de Conexão e Protocolo de Comunicação

Endpoint determinístico da loja Xtreme:

`https://{shop}.myshopify.com/api/mcp`

Padrões técnicos críticos:

- Autenticação: Storefront MCP não exige OAuth 2.0 para operações públicas.
- Encapsulamento: `Content-Type: application/json` obrigatório.
- Mensagens: seguir JSON-RPC 2.0; usar `id` e `method` (ex: `tools/call`) para rastreio.

Exemplo de requisição (fetch):

```js
fetch("https://xtreme-store.myshopify.com/api/mcp", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    jsonrpc: "2.0",
    method: "tools/call",
    id: "tx-999",
    params: {
      name: "search_shop_catalog",
      arguments: { 
        query: "exemplo",
        context: "user_session_metadata" 
      }
    }
  })
});
```

## 3. Capacidades e Ferramentas do Catálogo e Suporte

Ferramentas e retorno esperado:

- `search_shop_catalog` (params: `query` req., `context` req.) → retorna nome, preço, moeda, `merchandise_id` (Variant ID), descrição, URLs.
- `search_shop_policies_and_faqs` (params: `query` req., `context` opc.) → retorna respostas diretas sobre políticas e FAQs.

Nota: obrigar grounding — o agente só deve usar dados retornados por estas ferramentas.

## 4. Gestão Transacional: Operações de Carrinho (Cart Management)

- Persistência: `cart_id` mantém sessão; se ausente, `update_cart` gera novo `cart_id`.
- Itens: `update_cart` usa array `add_items` com `merchandise_id` e `quantity`.
- Remover item: definir `quantity: 0`.
- CTA: ambas as ferramentas retornam `checkout_url` — apresentar como link destacado.

## 5. Guia de Integração no Agente de IA Conversacional Xtreme

Plano faseado:

1. Mapeamento de Domínio: definir `xtreme-store.myshopify.com` para construção de endpoints.
2. Descoberta de Ferramentas: usar `tools/list` para introspecção de esquemas.
3. Injeção de Metadados: passar `context` com histórico de sessão e intenções.
4. Grounding de Links: formatar `URL` retornada como hiperligações Markdown (`[Finalizar Compra](checkout_url)`).

## 6. Considerações de Segurança e Performance

- Conformidade: respeitar `Shopify API License and Terms of Use`.
- Rate Limits: implementar lógica de retry/backoff para `429`.
- Tratamento de Exceções: gerir mensagens genéricas de erro sem expor detalhes internos.

---

Este relatório define a integração Storefront MCP e as práticas para operar o agente Xtreme com grounding rigoroso e fluxos de compra eficientes.
