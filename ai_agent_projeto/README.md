# Agente AI para Consulta em Linguagem Natural - ANTAQ BigQuery

Documentação necessária para desenvolver um sistema de consulta aos dados do BigQuery usando linguagem natural (LangChain/LangGraph).

## Conteúdo

1. [Configuração BigQuery](./01_bigquery_config.md) - Conexão e configuração do BigQuery
2. [Esquema das Tabelas](./02_schema_tabelas.md) - Estrutura completa das tabelas
3. [Domínio de Negócio](./03_dominio_negocio.md) - Conceitos e regras de negócio ANTAQ
4. [Views Consultáveis](./04_views_consultaveis.md) - Views disponíveis para consulta
5. [Exemplos de Perguntas-SQL](./05_exemplos_perguntas_sql.md) - Pares pergunta/SQL para treinamento
6. [Guia de Desenvolvimento](./06_guia_desenvolvimento.md) - Referências técnicas e implementação

## Configuração BigQuery

```
Project ID: antaqdados
Dataset: br_antaq_estatistico_aquaviario
Location: US
```

## Tabelas Principais

| Tabela | Descrição | Chave Primária |
|--------|-----------|----------------|
| `atracacao` | Operações de atracação de navios | `id_atracacao` |
| `carga` | Movimentação de cargas | `id_carga` |
| `instalacao_origem` | Instalações portuárias de origem | `origem` |
| `instalacao_destino` | Instalações portuárias de destino | `destino` |
| `mercadoria_carga` | Catálogo de mercadorias | `cd_mercadoria` |
| `mercadoria_carga_conteiner` | Mercadorias conteinerizadas | `cd_mercadoria_conteinerizada` |
| `taxa_ocupacao` | Taxa de ocupação de berços | `idberco`, `dia_taxa_ocupacao` |

## Views Recomendadas para Consulta

Para o agente AI, recomenda-se usar as views validadas:

- `v_carga_oficial_antaq` - Carga segundo metodologia oficial ANTAQ
- `v_carga_metodologia_oficial` - View com regras oficiais
- `v_atracacao_validada` - Atracação com FK validada
- `v_carga_validada` - Carga com relacionamentos validados

## Restrições de Segurança

- **Apenas SELECT** - O agente deve executar apenas consultas de leitura
- **Limite de linhas** - Limitar resultados (ex: MAX 10.000 linhas)
- **Validação de sintaxe** - Verificar se não há comandos DML/DLL
- **Timeout** - Definir timeout máximo para queries (ex: 60 segundos)

## Próximos Passos

Para desenvolver o protótipo em um novo repositório:

1. Criar projeto Python com dependências LangChain/LangGraph
2. Configurar autenticação BigQuery (service account)
3. Implementar recuperação de schema do BigQuery
4. Criar agente com LangGraph ou LangChain
5. Treinar/adaptar com exemplos do domínio ANTAQ

## Referências

- [LangGraph SQL Agent](https://docs.langchain.com/oss/python/langgraph/sql-agent)
- [Build Agentic Workflow for BigQuery](https://medium.com/google-cloud/build-an-agentic-workflow-for-your-bigquery-data-using-langgraph-and-gemini-947d0a951a45)
- [NL2SQL com BigQuery e Gemini](https://cloud.google.com/blog/products/data-analytics/nl2sql-with-bigquery-and-gemini)
