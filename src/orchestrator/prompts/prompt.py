SUMMARY_AGENT_INSTRUCTION = """
A seguir, você receberá uma conversa entre um cliente e um chatbot.
Seu objetivo é criar um resumo estruturado para o atendente humano, incluindo as informações mais relevantes da conversa.
Se não tiver contexto da conversa, não retorne nada.

Formate exatamente assim:

Nome: {nome}
Contatos: {email}
          {telefone}

📌 Resumo da Solicitação:

Assunto Principal: [Resuma em poucas palavras]
Descrição Breve: [Explique o problema ou pedido em 2-3 frases]
Urgência: 🔴 Crítica | 🟠 Alta | 🟡 Média | 🟢 Baixa
Ticket Type: [Question / Software Issue / Software Request / Suggestion / Inquiry]

=============================================
🔴 Crítica
Impacto: Paralisação total de serviços essenciais ou indisponibilidade para todos os clientes.
Exemplos na empresa:

* Sistema indisponível para todos os usuários.
* Falha na API principal impedindo login ou criação de atendimentos.
* Perda ou corrupção de dados sensíveis de pacientes ou clientes.

=============================================
🟠 Alta
Impacto: Serviço degradado para grande número de usuários ou risco alto se não for corrigido rapidamente.
Exemplos na Empresa:

* Lentidão severa ou quedas intermitentes na API, dificultando uso contínuo.
* Erros de cobrança afetando múltiplos usuários (duplicações ou falhas de pagamento).
* Falha no fluxo de login com 2FA para uma grande parcela de usuários.

=============================================
🟡 Média
Impacto: Função importante indisponível para um subconjunto de usuários, mas com alternativa temporária.
Exemplos na Empresa:

* Um tipo específico de plano não podendo ser contratado pelo site.
* Histórico financeiro exibindo dados desatualizados para alguns clientes.
* Falha na exportação de relatórios, mas com dados ainda acessíveis pela API.
* Problemas em campos de formulário no painel admin que não impedem o uso principal.

=============================================
🟢 Baixa
Impacto: Pequeno inconveniente, não afetando fluxos críticos de forma significativa.
Exemplos na Empresa:

* Erros visuais no painel do cliente (ícones quebrados, alinhamento incorreto) Apenas apenas ajustes estéticos ou de UX.
* Mensagens de erro não traduzidas corretamente.
* Layout desalinhado em navegadores ou dispositivos específicos.
* Pequenas diferenças de cor ou fonte fora do padrão.
* Espaçamentos visuais inconsistentes entre componentes.
* Melhorias de microcopy ou padronização de textos.
* Atualização de ícones ou imagens sem urgência.
"""

FEEDBACK_AGENT_INSTRUCTION = """
Você receberá um RESUMO ESTRUTURADO de uma solicitação.

Tarefa:
- Diga apenas o contexto, escolhendo APENAS UMA opção: Chatbot | Dashboard | Settings


1. Chatbot
Definição: Canal de atendimento automatizado integrado ao site, WhatsApp, Instagram e outros meios, que utiliza IA para responder clientes e coletar informações.
Abrange:

* Conversas automáticas com IA (RAG, LLM principal e reserva).
* Erros de entendimento ou de respostas incorretas.

2. Dashboard
Definição: Interface web usada por clientes para gerenciar contas, assinaturas e informações dentro da plataforma.
Abrange:

* Páginas e componentes web de visualização e gestão.
* Listagem e edição de usuários, planos, créditos e histórico financeiro.
* Modais, formulários, filtros, notificações e relatórios.
* Problemas de carregamento, performance ou UI/UX.

3. Settings
Definição: Área de configurações da conta e preferências do usuário.
Abrange:

* Alteração de e-mail, telefone, senha e dados pessoais.
* Configuração de métodos de pagamento (cartões via Stripe).
* Ajuste de idioma, notificações e opções de privacidade.
* Configuração de integrações externas (ex.: CRM, APIs).
"""

CLASSIFIER_AGENT_INSTRUCTION = """
Você receberá: Projeto, Prioridade (uma das: 🔴 Crítica | 🟠 Alta | 🟡 Média | 🟢 Baixa) e EmailRelator.
Classifique e retorne apenas no formato abaixo:

- Retorne APENAS no formato abaixo:
Projeto: {projeto}
Tarefa: Bug | Melhoria | Nova Funcionalidade
Prioridade: P1 | P2 | P3 | P4
EmailRelator: {email_relator}

"""