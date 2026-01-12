# Projeto de Pesquisa: Desenvolvimento de Agente Inteligente para Consulta em Linguagem Natural de Dados Governamentais de Transporte Aquaviário

---

## 1. Identificação do Projeto

**Título:** Agente Inteligente Baseado em LLM para Consulta em Linguagem Natural de Dados da ANTAQ

**Área de Conhecimento:** Ciência da Computação / Inteligência Artificial

**Subárea:** Processamento de Linguagem Natural / Engenharia de Prompt / Agentes de IA

**Linha de Pesquisa:** Sistemas de Informação Inteligentes e Interfaces Conversacionais

**Duração Prevista:** 12 meses

---

## 2. Introdução e Contextualização

### 2.1 Contextualização

A Agência Nacional de Transportes Aquaviários (ANTAQ) é o órgão regulador do setor de transporte aquaviário no Brasil, responsável por coletar, processar e disponibilizar dados estatísticos sobre a movimentação de cargas nos portos brasileiros. Estes dados são fundamentais para:

- Formulação de políticas públicas de transporte e logística
- Planejamento estratégico do setor portuário
- Análises de competitividade e eficiência portuária
- Pesquisas acadêmicas sobre comércio exterior e logística

No entanto, o acesso a estas informações atualmente requer:

1. Conhecimento técnico da linguagem SQL (Structured Query Language)
2. Familiaridade com a estrutura e esquema do banco de dados BigQuery
3. Compreensão da metodologia oficial da ANTAQ para filtragem de dados válidos
4. Uso de ferramentas especializadas de Business Intelligence

### 2.2 Problema de Pesquisa

A barreira técnica para acesso aos dados da ANTAQ limita sua utilização por:

- **Decisores políticos** que não possuem conhecimento técnico em SQL
- **Pesquisadores** de áreas não técnicas (economia, relações internacionais, logística)
- **Empresários do setor** que necessitam de informações rápidas para tomada de decisão
- **Jornalistas** que precisam acessar dados para embasar reportagens

O problema central é: **Como tornar acessíveis dados governamentais complexos para usuários não técnicos através de interfaces em linguagem natural?**

### 2.3 Justificativa

**Relevância Social:**
- Democratização do acesso a dados públicos governamentais
- Transparência e accountability no setor de transportes
- Apoio à tomada de decisões baseada em evidências

**Relevância Acadêmica:**
- Contribuição para o estado da arte em Text-to-SQL
- Aplicação de técnicas de RAG (Retrieval-Augmented Generation) em domínio específico
- Pesquisa sobre engenharia de prompt para agentes de IA

**Relevância Econômica:**
- Redução de custos de treinamento em SQL/Business Intelligence
- Agilidade na obtenção de insights para decisões empresariais
- Melhoria na eficiência do setor portuário brasileiro

---

## 3. Objetivos

### 3.1 Objetivo Geral

Desenvolver e validar um agente de inteligência artificial capaz de interpretar consultas em linguagem natural sobre dados de transporte aquaviário e convertê-las automaticamente em queries SQL executáveis no BigQuery, retornando resultados formatados e insights acionáveis.

### 3.2 Objetivos Específicos

1. **Levantamento de Requisitos**
   - Mapear os schemas do BigQuery da ANTAQ
   - Identificar as regras de validação da metodologia oficial
   - Catalogar os tipos de consultas mais frequentes

2. **Desenvolvimento do Sistema**
   - Implementar arquitetura baseada em LangGraph para orquestração do agente
   - Criar módulo de metadados para descrição semântica do esquema
   - Desenvolver sistema RAG para recuperação de exemplos relevantes
   - Implementar camada de segurança e validação de SQL

3. **Validação e Avaliação**
   - Definir métricas de avaliação (precisão SQL, satisfação do usuário)
   - Realizar testes com usuários reais dos diversos perfis
   - Comparar performance com abordagens tradicionais (SQL direto, BI tools)

4. **Disseminação**
   - Publicar artigos em periódicos e congressos da área
   - Disponibilizar o código como open source
   - Documentar a metodologia para replicação em outros domínios

---

## 4. Referencial Teórico

### 4.1 Text-to-SQL (NL2SQL)

O problema de converter linguagem natural em SQL é estudado desde os anos 1970, com avanços significativos recentes devido aos Large Language Models (LLMs).

**Trabalhos Seminais:**
- Zhong et al. (2020) - Spider Dataset: benchmark para Text-to-SQL
- Scholak et al. (2021) - Schema-aware denoising for Text-to-SQL
- Pourreza & Rafiei (2023) - Impact of LLMs on Text-to-SQL

### 4.2 Agentes de IA com LangGraph

**Conceitos Chave:**
- **State Machines:** Estados, transições e loops em workflows de IA
- **Tool Use:** Capacidade de LLMs utilizarem ferramentas externas
- **Multi-step Reasoning:** Decomposição de problemas complexos

**Referências:**
- LangGraph Documentation (2024)
- ReAct Prompting (Yao et al., 2022)
- Chain-of-Thought Reasoning (Wei et al., 2022)

### 4.3 Retrieval-Augmented Generation (RAG)

Técnica que combina recuperação de informações relevantes com geração de resposta:

- Lewis et al. (2020) - Introdução ao RAG
- Mallen et al. (2022) - RAG para domínios especializados
- Especificamente para Text-to-SQL: Few-shot learning com exemplos similares

### 4.4 Engenharia de Prompt e Metadados

Uso de metadados semânticos para melhorar compreensão do esquema:

- Descrições de colunas e tabelas
- Categorização de campos (métricas, dimensões, filtros)
- Templates de queries por tipo de análise

---

## 5. Metodologia

### 5.1 Abordagem Metodológica

O projeto adota uma abordagem **Design Science Research** (Hevner et al., 2004), caracterizada pela construção e avaliação de artefatos tecnológicos para resolver problemas práticos.

### 5.2 Fases da Pesquisa

#### Fase 1: Levantamento e Análise (Mês 1-2)

**Atividades:**
- Estudo do esquema BigQuery da ANTAQ
- Entrevistas com usuários dos dados (técnicos e não-técnicos)
- Catalogação de consultas SQL típicas
- Identificação de padrões de análise mais comuns

**Deliverables:**
- Documentação do esquema de dados
- Catálogo de metadados semânticos
- Taxonomia de tipos de consultas

#### Fase 2: Projeto da Arquitetura (Mês 3)

**Componentes Principais:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Apresentação                    │
│                   (Streamlit - Interface Web)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Camada do Agente (LangGraph)              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Setup    │  │Retrieve  │  │Generate  │  │Validate  │    │
│  │ Schema   │  │Examples  │  │SQL       │  │SQL       │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│       │              │              │              │         │
│       └──────────────┴──────────────┴──────────────┘         │
│                        │                                     │
│                   ┌────▼────┐  ┌─────────┐                   │
│                   │ Execute │  │ Format  │                   │
│                   │ SQL     │  │ Answer  │                   │
│                   └─────────┘  └─────────┘                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Abstração LLM                    │
│              (LLMFactory - Multi-Provedor)                   │
│  ┌────────────────────────────────────────────────────┐     │
│  │           LLM_PROVIDER=openai  │  vertexai         │     │
│  │                    │                     │           │     │
│  │              ┌─────▼─────┐         ┌─────▼─────┐    │     │
│  │              │ ChatOpenAI │         │ChatVertexAI│   │     │
│  │              │ text-emb.. │         │text-gecko..│   │     │
│  │              └────────────┘         └────────────┘    │     │
│  └────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Serviços                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Metadata     │  │ RAG / Vector │  │ Security     │      │
│  │ Helper       │  │ Store        │  │ Validator    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Camada de Dados                           │
│              (BigQuery - ANTAQ Dataset)                      │
└─────────────────────────────────────────────────────────────┘
```

#### Fase 3: Implementação do Core (Mês 4-6)

**Módulo de Metadados:**
- Tabela `dicionario_dados` em BigQuery
- Classe `MetadataHelper` com métodos:
  - `get_schema_for_prompt()` - Descrição do esquema para LLM
  - `explain_column()` - Explicação de coluna específica
  - `search_columns()` - Busca por palavras-chave
  - `get_official_filters()` - Filtros metodologia ANTAQ
  - `suggest_query_template()` - Templates por tipo de análise

**Módulo de Dados Referenciais:**
- `ReferentialHelper` para nomes amigáveis
- Mapeamento de códigos (UN/LOCODE) para nomes de portos
- Catálogo de mercadorias

**Módulo RAG:**
- Vector Store em BigQuery para exemplos Q/A
- Busca semântica para recuperação de exemplos similares
- Few-shot learning dinâmico

**Grafo LangGraph:**
```
setup_schema → retrieve_examples → generate_sql → validate_sql
                                                          │
                                              ┌───────────┘
                                              │
                                    [valid?]──YES──execute_sql
                                              │
                                    generate_final_answer
```

#### Fase 4: Interface de Usuário (Mês 7)

**Funcionalidades:**
- Aba Chat: Interface conversacional
- Aba Overview: Dashboard interativo para Porto de Santos
- Histórico de consultas
- Visualização de SQL gerado

#### Fase 5: Testes e Validação (Mês 8-10)

**Métricas de Avaliação:**

| Métrica | Descrição | Target |
|---------|-----------|--------|
| Precisão SQL | Queries sintaticamente corretas | >90% |
| Precisão Semântica | Queries que retornam resultado correto | >80% |
| Satisfação Usuário | Avaliação subjetiva (1-5) | >4.0 |
| Tempo Resposta | Tempo médio por consulta | <10s |
| Cobertura | % de tipos de consulta suportados | >70% |

**Protocolo de Teste:**
1. Conjunto de teste com 100 questões representativas
2. Avaliação por especialista em SQL
3. Teste com usuários reais (n=20, perfis variados)
4. Comparação com baseline (ChatGPT sem contexto)

#### Fase 6: Refinamento e Documentação (Mês 11-12)

- Iterações baseadas em feedback
- Documentação técnica completa
- Preparação de artigos científicos

### 5.3 Técnicas e Tecnologias Utilizadas

Esta seção apresenta de forma detalhada as técnicas e tecnologias empregadas no desenvolvimento do agente inteligente, fundamentando as escolhas técnicas e suas implicações para a pesquisa.

#### 5.3.1 Large Language Models (LLMs) e o Paradigma Transformer

Os Large Language Models representam uma ruptura paradigmática no campo de Processamento de Linguagem Natural (PNL), baseados na arquitetura Transformer introduzida por Vaswani et al. (2017). Esta arquitetura revolucionou o campo ao mecanismos de **self-attention** que permitem ao modelo capturar dependências contextuais de longo alcance em sequências textuais, superando as limitações das arquiteturas recorrentes anteriores (RNNs, LSTMs).

**Arquitetura Multi-Provedor:** Este projeto implementa uma **camada de abstração** que permite o uso de múltiplos provedores de LLM através de um padrão *Factory*, facilitando comparações e troca de provedores sem modificação de código. Os provedores suportados são:

1. **OpenAI GPT-4o-mini:** Provedor atual (configuração padrão)
   - Inferência rápida e custo-benefício excelente
   - Suporte nativo a function calling
   - Contexto de 128K tokens
   - Modelo: `gpt-4o-mini` (LLM) + `text-embedding-3-small` (embeddings)

2. **Google Vertex AI Gemini 1.5 Flash:** Provedor alternativo
   - Janela de contexto de até 1 milhão de tokens
   - Inferência eficiente com custos reduzidos
   - Multimodalidade embutida (texto, código, imagens)
   - Modelo: `gemini-1.5-flash` (LLM) + `textembedding-gecko@003` (embeddings)

**Padrão Factory para Abstração:** O módulo `src/llm/` implementa uma camada de abstração que:

```python
from src.llm import LLMFactory

# O provedor é determinado pela variável de ambiente LLM_PROVIDER
llm = LLMFactory.get_llm()          # Retorna ChatOpenAI ou ChatVertexAI
embeddings = LLMFactory.get_embeddings()  # Retorna OpenAIEmbeddings ou VertexAIEmbeddings

# Validação de configuração
validation = LLMFactory.validate_configuration()
# {'valid': True, 'provider': 'openai', 'errors': [], 'warnings': []}
```

**Benefícios da Arquitetura Multi-Provedor:**

- **Portabilidade:** Código independente de provedor específico
- **Comparação:** Facilita benchmarks entre GPT-4o-mini e Gemini
- **Resiliência:** Alternância rápida em caso de indisponibilidade
- **Custo-Benefício:** Escolha de provedor baseada em custos de API
- **Compatibilidade Retroativa:** Defaults para OpenAI se `LLM_PROVIDER` não definido

**Mecanismo de Function Calling:** Ambos os provedores suportam nativamente *tool calling* ou *function calling*, padrão essencial para implementação de agentes que necessitam interagir com APIs externas (BigQuery neste caso). O modelo é capaz de decidir autonomamente quando e qual ferramenta utilizar, uma capacidade que emerge do treinamento em larga escala com código e descrições de APIs.

#### 5.3.2 Orquestração de Agentes com LangGraph

**LangGraph** é uma biblioteca construída sobre LangChain projetada especificamente para criação de agentes stateful com workflows complexos. Diferente de abordagens anteriores baseadas em cadeias lineares (chains), LangGraph permite modelar o comportamento do agente como um **grafo de estados finitos** (finite state machine), onde cada nó representa uma função ou etapa de processamento e as arestas representam transições condicionais.

**Fundamentação Teórica:** A orquestração baseada em grafos fundamenta-se no paradigma **ReAct** (Reasoning + Acting) proposto por Yao et al. (2022). Neste paradigma, o LLM alternaria entre dois modos: (1) *reasoning* - gerar pensamentos intermediários ou planos; e (2) *acting* - executar ações através de ferramentas. Esta abordagem supera o paradigma anterior de *Chain-of-Thought* (Wei et al., 2022) ao permitir que o modelo interaja dinamicamente com o ambiente, observe resultados e ajuste sua estratégia.

**Arquitetura do Grafo:** O grafo implementado neste projeto consiste nos seguintes estados e transições:

```
[START] → setup_schema_node → retrieve_examples_node → generate_sql_node
                                                    ↓
                                            validate_sql_node
                                                    ↓
                                          [condicional: valid?]
                                              /              \
                                          [SIM]            [NÃO]
                                            ↓                 ↓
                                    execute_sql_node    generate_sql_node
                                            ↓                 (retry)
                                  format_answer_node
                                            ↓
                                          [END]
```

Cada nó do grafo é uma função assíncrona que recebe o estado atual do agente (um Pydantic model), executa operações e retorna atualizações parciais do estado. Este padrão permite:

- **Recuperação de Erros:** Nós podem detectar falhas (SQL inválido) e retry automaticamente
- **Cache Inteligente:** O schema do BigQuery é carregado apenas uma vez e reutilizado
- **Rastreamento:** Cada transição é logada para debug e análise
- **Extensibilidade:** Novos nós (ex: gerador de gráficos) podem ser adicionados sem refatoração completa

**Gestão de Estado:** O estado do agente é implementado através de modelos Pydantic fortemente tipados, garantindo validação em tempo de desenvolvimento e documentação automática. Campos incluem: mensagens do usuário, SQL gerado, resultados da execução, erro (se houver), e configurações como limite de linhas.

#### 5.3.3 Retrieval-Augmented Generation (RAG) para Domínio Específico

RAG (Lewis et al., 2020) é uma técnica que combina **recuperação de informação** com **geração de texto** para superar limitações de LLMs: conhecimento estático (data de corte do treinamento) e alucinações. Em vez de treinar ou fine-tunar o modelo (processo custoso e técnico), RAG injeta contexto relevante *no momento da inferência*.

**Vector Store Semântico:** Este projeto implementa um sistema RAG onde cada exemplo de pergunta-SQL é convertido em um **embedding** (representação vetorial densa) através de modelos como `text-embedding-004` do Google. Estes embeddings são armazenados no BigQuery Vector Store, permitindo busca semântica eficiente.

Quando o usuário faz uma pergunta, o sistema:
1. Gera o embedding da pergunta do usuário
2. Executa busca de similaridade (cosine similarity) no vector store
3. Recupera os k exemplos mais similares (k=3 típico)
4. Injeta estes exemplos no prompt do LLM como few-shot learning

**Vantagens sobre Fine-Tuning:**
- **Atualização Dinâmica:** Novos exemplos podem ser adicionados sem retrtreino
- **Interpretabilidade:** É possível inspecionar quais exemplos foram recuperados
- **Custo-Benefício:** Não requer GPUs dedicadas para treinamento
- **Explicabilidade:** Decisões do modelo podem ser justificadas pelos exemplos recuperados

#### 5.3.4 Engenharia de Metadados e Schema Awareness

Uma das principais dificuldades em Text-to-SQL para bancos de dados reais é o **gap semântico** entre nomes de tabelas/colunas (frequentemente crípticos ou abreviados) e a linguagem natural dos usuários. Este projeto aborda este problema através de duas estratégias complementares:

**1. Tabela de Dicionário de Dados:** Criou-se uma tabela dedicada `antaq_metadados.dicionario_dados` que armazena metadados semânticos sobre cada coluna:

| Campo | Descrição | Exemplo |
|-------|-----------|---------|
| `tabela` | Nome da tabela | `v_carga_metodologia_oficial` |
| `coluna` | Nome da coluna | `vlpesocargabruta_oficial` |
| `descricao` | Descrição em português | "Peso bruto da carga em toneladas (métrica oficial)" |
| `tipo_dado` | Tipo de dado | `FLOAT64` |
| `valores_possiveis` | Restrições/domínio | `NULL` |
| `categoria` | Categoria semântica | `Métrica`, `Temporal`, `Localização`, `Operação` |
| `tags` | Palavras-chave | `['peso', 'tonelada', 'volume', 'métrica principal']` |

Esta estrutura permite consultas dinâmicas como: "Busque colunas relacionadas a 'peso' e 'exportação'" retornando campos relevantes com suas descrições.

**2. Categorização Semântica:** Colunas são categorizadas em classes que guiam a geração de SQL:
- **Métricas:** Campos numéricos agregáveis (SUM, AVG) como `vlpesocargabruta_oficial`
- **Dimensões Temporais:** Campos de data para filtros e agrupamentos
- **Dimensões Geográficas:** Porto, UF, país para análises espaciais
- **Códigos de Negócio:** Mercadorias, sentidos (importação/exportação)

Esta categorização permite ao sistema gerar templates apropriados: uma pergunta sobre "ranking de portos" resultaria em SQL com `GROUP BY porto, ORDER BY SUM(peso) DESC`, enquanto uma "evolução mensal" geraria `GROUP BY ano, mes ORDER BY ano, mes`.

**Ferramentas LangChain para Metadados:** Quatro ferramentas estruturadas (tools) foram criadas para o agente:
- `explain_column(table, column)`: Explica uma coluna com dicas de uso
- `search_columns(keywords)`: Busca colunas por palavras-chave
- `get_official_filters()`: Retorna filtros oficiais da metodologia ANTAQ
- `suggest_query_template(intent)`: Sugere template SQL baseado na intenção

O LLM pode invocar estas ferramentas autonomamente durante o processo de geração de SQL, enriquecendo seu entendimento do esquema.

#### 5.3.5 Validação de SQL e Segurança

A geração automática de SQL por LLMs introduz riscos significativos: o modelo pode gerar código malicioso, queries excessivamente custosas, ou sintaxe inválida. Este projeto implementa uma estratégia de defesa em profundidade (defense-in-depth):

**Validação Sintática:**
- Análise léxica para detectar palavras-chave proibidas (`DROP`, `DELETE`, `INSERT`, `UPDATE`)
- Verificação de prefixo permitido (queries devem começar com `SELECT` ou `WITH`)
- Validação básica de parênteses balanceados

**Validação Semântica:**
- Verificação de existência de tabelas e colunas usando INFORMATION_SCHEMA
- Tipagem de dados (ex: não comparar string com int)
 Detecção de agregações sem GROUP BY correspondente

**Limites de Recursos:**
- `MAX_ROWS = 1000`: Prevenir exaustão de memória
- `TIMEOUT = 60s`: Prevenir queries longas
- `MAX_BYTES_BILLED = 10GB`: Prevenir custos excessivos no BigQuery

**Injeção de SQL:** Como queries são montadas com f-strings Python, existe risco de SQL injection. Mitigação:
- Validação de inputs do usuário
- Uso de parâmetros nomeados do BigQuery quando possível
- Sanitização de nomes de tabelas/colunas

#### 5.3.6 BigQuery como Data Warehouse

**Google BigQuery** é um data warehouse serverless, altamente escalável e totalmente gerenciado. Diferente de bancos de dados tradicionais (PostgreSQL, MySQL), BigQuery otimiza para cargas analíticas (OLAP) ao invés de transacionais (OLTP).

**Características Relevantes:**

**Arquitetura Columnar:** Dados são armazenados por coluna ao invés de por linhas. Para queries analíticas que tipicamente leem poucas colunas mas muitas linhas (ex: `SELECT ano, SUM(peso) FROM ... GROUP BY ano`), isso reduz drasticamente I/O. A view `v_carga_metodologia_oficial` possui dezenas de colunas, mas queries típicas acessam apenas 5-10.

**Processamento Distribuído:** Queries são automaticamente partitionadas e executadas em paralelo em milhares de nós, permitindo processar petabytes de dados em segundos. O modelo *pay-per-query* (cobrança por dados processados) elimina necessidade de provisionar infraestrutura.

**BigQuery ML:** Capacidade de executar modelos de ML diretamente no banco de dados usando SQL (ex: `SELECT * FROM ML.PREDICT(MODEL 'dataset.model', ...)`). Embora não utilizado neste projeto, abre possibilidades futuras como detecção de anomalias em padrões de carga.

**INFORMATION_SCHEMA:** BigQuery expõe metadados através de tabelas padronizadas INFORMATION_SCHEMA (compatível com padrão ANSI SQL), permitindo queries introspectivas como:
```sql
SELECT column_name, data_type
FROM `antaqdados.br_antaq_estatistico_aquaviario.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'v_carga_metodologia_oficial'
```

**Vector Store Nativo:** BigQuery recentemente adicionou capacidades de busca vetorial through `VECTOR<>` type e função `COSINE_DISTANCE()`, eliminando necessidade de serviços externos (Pinecone, Milvus). Isso simplifica a arquitetura: tudo permanece no mesmo ecossistema Google Cloud.

#### 5.3.7 Interface Web com Streamlit

**Streamlit** é um framework Python para criação de interfaces web para projetos de Machine Learning e Data Science. Diferente de frameworks tradicionais (Flask, Django) que exigem conhecimento de HTML/CSS/JavaScript e separação frontend/backend, Streamlit permite criar UIs puramente em Python através de scripts reativos.

**Vantagens para Prototipagem Rápida:**
- **Turnaround Curtíssimo:** Mudanças na UI refletem em save-and-refresh (<1s)
- **Componentes Prontos:** `st.text_input()`, `st.dataframe()`, `st.metric()`, `st.chat()`
- **Reatividade Automática:** Quando o usuário interage, o script é re-executado do topo

**Limitações e Mitigações:**
- **Statelessness:** Cada interação reexecuta o script. Mitigação: `st.session_state` para persistência
- **Escalabilidade:** Não adequado para milhares de usuários simultâneos. Mitigação: Planejado reescrever frontend em React/Next.js para produção
- **Customização Limitada:** Estilos são difíceis de customizar. Mitigação: CSS injection via `st.markdown(unsafe_allow_html=True)`

**Para este projeto**, Streamlit é ideal como MVP (Minimum Viable Product), permitindo iterações rápidas com feedback dos stakeholders sem sobrecarregar o desenvolvimento com boilerplate de frontend tradicional.

#### 5.3.8 Materiais e Métodos

**Tecnologias:**

**Framework e Orquestração:**
- Python 3.11+ (type hints, pattern matching, asyncio nativo)
- LangGraph >= 0.2.0 (orquestração de agentes stateful)
- LangChain >= 0.3.0 (framework de agentes e tools)
- LangChain OpenAI >= 0.2.0 (integração OpenAI)
- LangChain Google VertexAI >= 1.0.0 (integração Google Cloud)
- LangChain Google Community >= 1.0.0 (BigQuery Vector Store)

**LLM e Embeddings (Multi-Provedor):**
- OpenAI GPT-4o-mini (configuração padrão atual)
  - LangChain: `ChatOpenAI`
  - Embeddings: `text-embedding-3-small`
- Google Vertex AI Gemini 1.5 Flash (alternativo)
  - LangChain: `ChatVertexAI`
  - Embeddings: `textembedding-gecko@003`

**Banco de Dados:**
- Google BigQuery (data warehouse analytical)
- BigQuery Vector Store (RAG com busca vetorial nativa)
- INTEGRATION_SCHEMA (metadados de esquema)

**Interface Web:**
- Streamlit 1.28+ (interface web reativa)
- Plotly 5.18+ (visualizações interativas)

**Dados Utilizados:**
- Dataset: `antaqdados.br_antaq_estatistico_aquaviario`
- Tabelas principais:
  - `v_carga_metodologia_oficial`: Carga segundo metodologia oficial ANTAQ
  - `v_atracacao_validada`: Atracação com FKs validadas
  - `instalacao_origem`: Catálogo de instalações de origem (portos)
  - `instalacao_destino`: Catálogo de instalações de destino (portos)
  - `mercadoria_carga`: Catálogo de mercadorias segundo classificação ANTAQ

**Módulos Implementados:**

```
src/
├── llm/                        # Multi-provedor LLM (NOVO)
│   ├── __init__.py            # LLMFactory, LLMConfig
│   ├── factory.py             # Factory pattern para seleção de provedor
│   ├── config.py              # Pydantic validation de configuração
│   └── providers/
│       ├── base.py            # Classes abstratas LLMProvider, EmbeddingProvider
│       ├── openai.py          # OpenAI implementation
│       └── vertexai.py        # VertexAI implementation
│
├── agent/                      # LangGraph agent
│   ├── graph.py               # State machine definition
│   ├── nodes.py               # Node implementations (usa LLMFactory)
│   ├── state.py               # AgentState (Pydantic)
│   ├── metadata_helper.py     # Schema awareness
│   ├── tools.py               # LangChain tools (explain_column, etc)
│   └── prompts.py             # System prompts
│
├── bigquery/
│   ├── client.py              # BigQuery client
│   ├── schema.py              # Schema retriever
│   ├── vector_store.py        # Vector store (usa LLMFactory)
│   └── referential_helper.py  # Friendly names lookup
│
└── rag/
    ├── embeddings.py          # Embeddings (usa LLMFactory)
    └── retriever.py           # ExampleRetriever
```

**Variáveis de Ambiente (Configuração):**

```bash
# Seleção de provedor (obrigatório)
LLM_PROVIDER=openai              # Options: openai, vertexai

# OpenAI (quando LLM_PROVIDER=openai)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small

# Google Vertex AI (quando LLM_PROVIDER=vertexai)
GOOGLE_CLOUD_PROJECT=saasimpacto
GOOGLE_CLOUD_REGION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
VERTEXAI_MODEL=gemini-1.5-flash
VERTEXAI_EMBEDDING_MODEL=textembedding-gecko@003

# Comum (opcional)
LLM_TEMPERATURE=0
LLM_MAX_TOKENS=1000
LLM_TIMEOUT=60
```

---

## 6. Cronograma

| Mês | Atividade | Responsável |
|-----|-----------|--------------|
| 1-2 | Levantamento de requisitos e análise de dados | Pesquisador |
| 3 | Projeto da arquitetura | Pesquisador + Orientador |
| 4-5 | Implementação MetadataHelper e RAG | Pesquisador |
| 5-6 | Implementação LangGraph e validação SQL | Pesquisador |
| 7 | Desenvolvimento interface Streamlit | Pesquisador |
| 8-9 | Testes técnicos e ajustes | Pesquisador |
| 9-10 | Validação com usuários | Pesquisador + Voluntários |
| 11 | Análise de resultados e refinamento | Pesquisador + Orientador |
| 12 | Documentação e artigos científicos | Pesquisador + Orientador |

---

## 7. Resultados Esperados

### 7.1 Produtos Técnicos

1. **Sistema Funcional**
   - Agente de IA para consulta em linguagem natural
   - Interface web interativa
   - Código-fonte documentado (open source)

2. **Documentação**
   - Documentação técnica completa
   - Manual de usuário
   - Metodologia replicável para outros domínios

### 7.2 Produtos Científicos

1. **Artigos para Periódicos**
   - "Text-to-SQL para Dados Governamentais Brasileiros"
   - "Metadata-Driven Schema Awareness for LLM Agents"
   - "Evaluation of Conversational Interfaces for Public Data"

2. **Artigos para Congressos**
   - ENIAC (Encontro Nacional de Inteligência Artificial)
   - SBBD (Simpósio Brasileiro de Banco de Dados)
   - CSBC (Congresso da Sociedade Brasileira de Computação)

### 7.3 Contribuições Teóricas

1. **Metodologia de Engenharia de Metadados**
   - Padrão para descrição semântica de schemas complexos
   - Taxonomia de tipos de análise em dados governamentais

2. **Arquitetura de Agentes Especializados**
   - Padrão para agentes RAG em domínios específicos
   - Estratégias de validação de SQL gerado por LLM

---

## 8. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|---------|-----------|
| LLM não compreende domínio específico | Média | Alto | Few-shot learning + metadados ricos |
| Queries SQL incorretas | Alta | Médio | Validador sintático + semântico |
| Performance insuficiente | Baixa | Médio | Cache + otimizações de prompt |
| Usuários não adotam solução | Média | Alto | Testes com usuários + UX refinada |
| Custos de API LLM altos | Média | Baixo | Cache + modelo custo-benefício |

---

## 9. Aspectos Éticos

**Privacidade e Dados:**
- Todos os dados são públicos (governamentais)
- Não há coleta de dados pessoais
- Transparência sobre limitações do sistema

**Responsabilidade:**
- Indicação clara de quando dados são oficiais
- Validação de SQL para evitar consultas maliciosas
- Limitação de recursos (max rows, timeout)

**Acessibilidade:**
- Interface em português brasileiro
- Suporte a linguagem natural informal
- Documentação bilíngue (português/inglês)

---

## 10. Orçamento Estimado

| Item | Custo (R$) | Justificativa |
|------|-----------|---------------|
| Credits Google Cloud (BigQuery, Vertex AI) | R$ 2.000 | 12 meses de desenvolvimento |
| Hardware adicional (se necessário) | R$ 1.500 | Memória/processamento |
| Publicação de artigos (fees) | R$ 1.200 | 2-3 artigos |
| Viagens para congressos | R$ 4.000 | 2 congressos nacionais |
| **TOTAL** | **R$ 8.700** | |

---

## 11. Referências Bibliográficas

### Papers Acadêmicos

1. Zhong, V., et al. (2020). "Semantic Parsing on Spider: A Figure of Speech?" *ACL 2020*.

2. Scholak, T., et al. (2021). "Comprehensively and accurately benchmarking semantic parsing for text-to-SQL." *EMNLP 2021*.

3. Lewis, P., et al. (2020). "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks." *NeurIPS 2020*.

4. Yao, S., et al. (2022). "ReAct: Synergizing Reasoning and Acting in Language Models." *ICLR 2023*.

5. Wei, J., et al. (2022). "Chain-of-Thought Prompting Elicits Reasoning in Large Language Models." *NeurIPS 2022*.

6. Hevner, A. R., et al. (2004). "Design Science in Information Systems Research." *MIS Quarterly*.

### Documentação Técnica

7. LangGraph Documentation. (2024). *https://langchain-ai.github.io/langgraph/*

8. BigQuery Documentation. (2024). *https://cloud.google.com/bigquery/docs*

9. ANTAQ. (2024). *Estatística Aquaviária - Metodologia Oficial*.

### Relatórios Governamentais

10. ANTAQ. (2023). *Anuário Estatístico do Transporte Aquaviário*.

---

## 12. Disseminação

### 12.1 Eventos Científicos

- **ENIAC 2025** - Encontro Nacional de Inteligência Artificial
- **SBBD 2025** - Simpósio Brasileiro de Banco de Dados
- **CSBC 2025** - Congresso da Sociedade Brasileira de Computação

### 12.2 Canais de Disseminação

- Repositório GitHub (código aberto)
- Blog técnico/artigos Medium
- Workshops com comunidade Python Brasil
- Apresentações em meetups de IA e Dados

### 12.3 Público-Alvo

- Comunidade acadêmica (pesquisadores em IA/NLP)
- Desenvolvedores de aplicações governamentais
- Gestores públicos de transporte
- Setor portuário e logístico

---

**Aprovado em:** ___/___/_____

**Assinatura do Pesquisador:** _______________

**Assinatura do Orientador:** _______________
