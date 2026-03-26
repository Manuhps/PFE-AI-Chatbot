# Investigação AI chatbot e Gorgias
# Esta investigação teve como objetivo analisar a arquitetura atual do projeto e, teve uma como referencias aos relatórios técnicos anteriores e a base do repositorio intellecta-shopify-app.

O foco desta investigação é perceber como a base atual do projeto suporta essa evolução e, em particular, de que forma a integração com o Gorgias reforça o suporte ao comerciante e aos clientes. Para isso, importa analisar:

- a estrutura das rotas e superfícies da aplicação;
- os serviços de backend já existentes;
- a camada de IA e orquestração já preparada;
- a persistência em MongoDB;
- a integração com ferramentas externas;
- o papel do Gorgias como camada de helpdesk e transição humana.

Em termos práticos, este relatório serve para ligar o que já existe no repositório com a visão de evolução para um chatbot de suporte e automação mais completo.
Tambem importante referir que tive acesso a dev store dashboard e a app instalada, o que me permitiu perceber melhor o fluxo de utilizador e as interações possíveis.

## 1. Visão Geral do Projeto e Objetivos

Este projeto consiste numa aplicação Shopify embutida (embedded), desenvolvida sobre a framework Remix, que representa a evolução de uma ferramenta administrativa para uma solução sofisticada de chatbot baseada em Inteligência Artificial. A arquitetura caracteriza-se por uma dualidade estratégica: enquanto a aplicação é executada e gerida no Shopify Admin (back-office), a sua inteligência e interface de conversação são projetadas para as superfícies de interação direta com o cliente, nomeadamente no Storefront e no Checkout.

Os objetivos centrais que norteiam a direção do produto são:

- Estabelecer uma ligação nativa entre a loja Shopify e um assistente de IA avançado.
- Utilizar dados granulares da loja e integrações externas como contexto enriquecido para as respostas da IA.
- Disponibilizar o assistente de forma ubíqua através do Storefront, Checkout e painel de Administração.
- Automatizar tarefas operacionais críticas, incluindo suporte ao cliente, vendas, gestão de integrações e assistência relacionada com pedidos.

## 2. Arquitetura de Software e Stack Tecnológica

A infraestrutura foi desenhada para garantir escalabilidade e uma integração profunda com as APIs do Shopify, utilizando uma stack moderna e tipada.

### Core Stack

| Componente | Tecnologia / Ferramenta |
| --- | --- |
| Framework | Remix (via Shopify CLI) |
| Bundler | Vite |
| Linguagem | TypeScript |
| Base de Dados | MongoDB |
| Autenticação | Shopify App Remix (App Bridge & Session Token Management) |

### Infraestrutura de Backend

A lógica de backend reside em `app/services`, onde se implementa a separação de responsabilidades necessária para um sistema de nível empresarial:

- `mongo.server.ts`: gere a persistência de dados e a conectividade com o MongoDB.
- `shopify.server.tsx`: configuração central para autenticação e comunicação com a API Shopify.
- `intellecta.server.tsx`: implementa a lógica de serviço específica do projeto e regras de negócio customizadas.
- `whatsapp.server.ts`: gere a lógica de comunicação e integração com o canal WhatsApp.
- `billing.server.ts`: responsável pela gestão de faturação e subscrições da aplicação.
- `composio.server.ts`: atua como a camada de integração para ferramentas de terceiros (CRM, e-mail, ferramentas de produtividade), facilitando fluxos OAuth e execução de ações externas.

## 3. Ecossistema de IA e Orquestração (LangGraph)

A inteligência da plataforma está concentrada na pasta `app/ai_services`, que serve como o motor de decisão e processamento de linguagem natural.

Os ficheiros fundamentais desta camada incluem:

- `config.server.js`: o nó central de configuração para todos os serviços e parâmetros de IA.
- `claude.server.js` e `groq.server.js`: implementações de acesso aos fornecedores de Large Language Models (LLM).
- `langgraph.server.js`: utilizado para a orquestração complexa de fluxos, permitindo a gestão de estado da conversação e a lógica de decisão para execução de ferramentas (tool calling).
- `streaming.server.js`: garante a entrega de respostas em tempo real para melhorar a experiência do utilizador.
- `tool.server.js` e `shopify-order-tools.server.js`: definem as capacidades acionáveis da IA, permitindo que esta interaja diretamente com os dados de pedidos da loja.

O LangGraph não se limita a gerar respostas; ele gere o grafo de conversação, decidindo quando deve invocar ferramentas específicas do Shopify ou quando deve escalar a interação para outros serviços.


### Theme App Extension (`extensions/chat-bubble/`)

Implementa o widget de chat na montra da loja (Storefront). É a interface principal de contacto que acompanha o cliente durante a navegação nos produtos, servindo como o primeiro ponto de triagem e assistência.

### Checkout Extension (`extensions/checkout-chat/`)

Focada no suporte conversacional durante a fase crítica de pagamento. Esta extensão consome a rota `checkout-chat._index.tsx` para fornecer assistência imediata, ajudando a converter vendas e reduzir o abandono do carrinho.

### Rotas Administrativas

Adicionalmente, o sistema utiliza rotas administrativas específicas para a gestão da inteligência:

- `_app.integrations._index.tsx`: gestão e monitorização de conectores externos.
- `_app.knowledge._index.tsx`: interface para gestão de conhecimento, onde o lojista alimenta a base de dados da IA.
- `_app.chat._index.tsx` e `_app.internal-chat._index.tsx`: superfícies de chat para interação direta e testes internos.

## 5. Integração Gorgias: Camada de Suporte e Transição Humana (Human Handoff)

O Gorgias é posicionado como o backend operacional de suporte, assegurando que a automação por IA nunca comprometa a qualidade do atendimento humano quando este é necessário.

### Fluxo de Trabalho de Transição (Handoff)

1. Interação Inicial: o cliente submete uma dúvida através do widget de chat.
2. Classificação de Intenção: o bot identifica se a questão é relativa a pedidos, reembolsos, reclamações ou suporte técnico.
3. Resolução Autónoma: se a resposta estiver disponível nos dados da loja ou base de conhecimento, o bot resolve a questão.
4. Escalonamento: caso a IA não consiga resolver ou detete necessidade de intervenção, cria ou atualiza um ticket no Gorgias.
5. Transferência de Contexto: o bot transmite o resumo da conversa, dados do cliente, contexto do pedido e o nível de urgência detetado.
6. Intervenção Humana: um agente assume o ticket na plataforma Gorgias, mantendo a continuidade do diálogo com o contexto completo.

### Vantagens da Integração Gorgias

- Suporte omnichannel: centralização de interações via e-mail, redes sociais e web chat num único fluxo.
- Triagem inteligente: organização automática de tickets baseada em sentimento, intenção ou valor do pedido.
- Consistência de respostas: partilha de macros e modelos de resposta entre a IA e os agentes humanos.
- Preservação do fallback: garante que casos complexos são sempre endereçados por especialistas.

### Ações para Melhorar a Camada Gorgias

- Criação de uma Base de Conhecimento Partilhada (Shared Knowledge Base): sincronizar as respostas da IA com as macros dos agentes.
- Monitorização de KPIs: rastrear taxas de resolução, deflexão (casos resolvidos apenas pela IA) e taxas de escalonamento.
- Deteção de Sentimento Proativa: identificar clientes insatisfeitos para priorização imediata no Gorgias.
- Sincronização Automática: injetar detalhes técnicos do pedido Shopify diretamente no contexto do ticket.

## 6. Gestão de Dados e Configuração do Ambiente

A estabilidade da aplicação embutida depende da gestão rigorosa de sessões e variáveis de ambiente.

As variáveis críticas identificadas são: `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`, `SHOPIFY_APP_URL`, `SHOPIFY_APP_NAME`, `MONGODB_URI`, `MONGODB_DATABASE`, `COMPOSIO_API_KEY`, `NODE_ENV`.

O MongoDB desempenha um papel fundamental como Session Storage, um componente crítico em aplicações Shopify embutidas para mitigar problemas com cookies de terceiros e garantir a persistência da autenticação. Além das sessões, é utilizado para armazenar o histórico de conversas (contexto) e a base de gestão de conhecimento (knowledge management).

## 7. Investigação Técnica e Linhas de Evolução

A investigação desta arquitetura indica que a solução não deve ser entendida apenas como um chatbot reativo, mas como uma camada de automação e suporte com capacidade de escalonamento, integração e enriquecimento contextual.

As principais áreas de investigação e validação são:

- Persistência de conhecimento: validar a eficácia da recuperação de informação (RAG) armazenada no MongoDB para respostas contextuais.
- Validação de streaming: testar a estabilidade do processamento de streaming de respostas para minimizar a latência no Storefront.
- Mapeamento de ferramentas (tools): expandir as capacidades da IA para incluir ações específicas sobre Catálogo de Produtos, Perfis de Clientes e gestão de Pedidos.
- Integração Gorgias: validar o fluxo de handoff e a sincronização de contexto entre o chatbot e a equipa humana de suporte.
- Otimização de UI: determinar a rota mais eficiente para a interface do chatbot, garantindo compatibilidade total com dispositivos móveis e restrições do Shopify App Bridge.

### Questões de investigação sugeridas/questões releventes para análise

Para orientar a análise técnica e a redação do relatório, as seguintes questões podem ser exploradas:

- Em que medida a estrutura atual do projeto já suporta um chatbot de IA multi-superfície?
- Quais os pontos do código que mais beneficiam de orquestração via LangGraph?
- Como deve ser feita a separação entre resolução automática e escalonamento para o Gorgias?
- Que tipos de tickets e anomalias devem ser tratados automaticamente pelo chatbot antes de haver handoff?
- Como garantir que o contexto transferido para o Gorgias é suficiente para reduzir repetição de trabalho humano?
- Qual a melhor combinação entre MongoDB, streaming e ferramentas externas para suportar respostas rápidas e consistentes?

### Contribuição esperada desta investigação

Esta investigação deve produzir uma visão clara sobre como a aplicação evolui de uma base Shopify embebida para uma solução de suporte inteligente, identificando:

- a arquitetura atual e o seu potencial de expansão;
- os pontos críticos de integração com IA e helpdesk;
- os benefícios operacionais da integração com Gorgias;
- os requisitos técnicos para suportar automação, contexto e continuidade de atendimento.
- para usos futuros, como analise e orientação para o desenvolvimento do projeto de estagio.
