# Análise: SmartQueryAssistant para ANTAQ AI Agent

## 📊 Resumo

O `SmartQueryAssistant` é um sistema de consultas inteligentes baseado em metadados do BigQuery. Foi analisado para identificar recursos úteis ao projeto ANTAQ AI Agent.

## ✅ Recursos Integrados

### 1. MetadataHelper (`src/agent/metadata_helper.py`)

Implementa as funcionalidades úteis do SmartQueryAssistant:

| Método | Descrição |
|--------|-----------|
| `has_column(table, column)` | Verifica se coluna existe usando INFORMATION_SCHEMA |
| `get_official_period_filter_sql()` | Filtro de período oficial (45 dias lag) |
| `get_official_methodology_filters_sql()` | Filtros da metodologia oficial ANTAQ |
| `load_metadata()` | Carrega metadados da tabela `dicionario_dados` |
| `search_columns(keywords)` | Busca colunas por palavras-chave |
| `explain_column(table, column)` | Explicação detalhada de coluna |
| `get_schema_for_prompt()` | Schema formatado para prompts LLM |
| `suggest_query_template(intent)` | Sugere template de query por intenção |

### 2. Filtros Oficiais ANTAQ

Implementados em `prompts.py`:

```python
## OFFICIAL FILTER TEMPLATE

WHERE c.isValidoMetodologiaANTAQ = 1
  AND c.vlpesocargabruta_oficial > 0
  AND LOWER(c.tipo_operacao_da_carga) IN (
      'movimentação de carga', 'apoio',
      'longo curso exportação', 'longo curso importação',
      'cabotagem', 'interior',
      'baldeação de carga nacional', 'baldeação de carga estrangeira de passagem'
  )
```

**Importância:**
- Apenas dados válidos pela metodologia oficial ANTAQ
- Exclui operações não-oficiais
- Garante consistência com dados publicados

### 3. Verificação Dinâmica de Colunas

```python
def has_column(self, table: str, column: str) -> bool:
    """Check if column exists using INFORMATION_SCHEMA"""
```

**Benefício:** Evita erros de queries com colunas que podem não existir em determinadas views.

## 📋 Recursos Não Integrados

| Recurso | Motivo |
|---------|--------|
| `interactive_assistant()` | Substituído pela interface Streamlit |
| `_suggest_weight_queries()` | Padrões já cobertos pelos exemplos RAG |
| Modo CLI | Interface web é mais adequada |

## 🔄 Próximos Passos

1. **Integrar MetadataHelper no agent nodes**
   - Usar `suggest_query_template()` no nó de geração de SQL
   - Usar `get_schema_for_prompt()` ao invés do schema hardcoded

2. **Adicionar suporte à tabela `dicionario_dados`**
   - Se a tabela existir no BigQuery, será usada automaticamente
   - Se não existir, usa schema hardcoded como fallback

3. **Atualizar exemplos RAG**
   - Incluir os filtros oficiais em todos os exemplos
   - Garantir consistência com metodologia ANTAQ

## 📝 Exemplo de Uso

```python
from src.agent.metadata_helper import get_metadata_helper

# No nó de geração de SQL
metadata_helper = get_metadata_helper()

# Obter filtros oficiais
official_filters = metadata_helper.get_official_methodology_filters_sql('c')

# Sugerir template baseado na intenção
template = metadata_helper.suggest_query_template("ranking de portos")
# Retorna template com placeholders para preencher
```

## 🎯 Impacto nas Queries

### Antes:
```sql
SELECT SUM(vlpesocargabruta_oficial)
FROM v_carga_metodologia_oficial
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
```

### Depois:
```sql
SELECT SUM(vlpesocargabruta_oficial)
FROM v_carga_metodologia_oficial
WHERE c.isValidoMetodologiaANTAQ = 1
  AND c.vlpesocargabruta_oficial > 0
  AND LOWER(c.tipo_operacao_da_carga) IN (
      'movimentação de carga', 'apoio',
      'longo curso exportação', 'longo curso importação',
      'cabotagem', 'interior',
      'baldeação de carga nacional', 'baldeação de carga estrangeira de passagem'
  )
  AND c.ano = 2024
```

**Diferença:** Filtros mais completos garantem apenas dados oficiais válidos.
