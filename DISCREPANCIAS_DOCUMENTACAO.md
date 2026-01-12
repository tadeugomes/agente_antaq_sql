# Mapeamento: Documentação Original vs Realidade BigQuery

## Data: 2025-12-31

## Problema Identificado

A documentação original na pasta `ai_agent_projeto/` foi baseada em tabelas brutas e esquemas teóricos. A view real `v_carga_metodologia_oficial` no BigQuery usa nomes de colunas e valores diferentes.

## Tabela de Mapeamento

| Documentação Original (Tabela Bruta) | BigQuery Real (v_carga_metodologia_oficial) | Status |
|--------------------------------------|---------------------------------------------|--------|
| **Tabela/View** | `carga` ou `v_carga_oficial_antaq` | `v_carga_metodologia_oficial` | ⚠️ **Usar view oficial** |
| **Coluna peso** | `peso_carga` | `vlpesocargabruta_oficial` | ⚠️ **Nome diferente** |
| **Coluna porto** | `nm_porto` | `porto_atracacao` | ⚠️ **Nome diferente** |
| **Coluna sentido** | `sentido_carga` | `sentido` | ⚠️ **Nome diferente** |
| **Valores sentido** | 'Importação', 'Exportação', 'Cabotagem' | 'Embarcados', 'Desembarcados' | ⚠️ **Valores diferentes** |
| **Coluna navegacao** | `tipo_navegacao` | `tipo_de_navegacao_da_atracacao` | ⚠️ **Nome diferente** |
| **Coluna mercadoria** | `cd_mercadoria` | `cdmercadoria` | ✅ **Similar** |
| **Filtro oficial** | `flagmcoperacaocarga = '1'` | `isValidoMetodologiaANTAQ = 1` | ⚠️ **Nome diferente** |
| **Tipo ano** | INT64 | INT64 | ✅ **Igual** |
| **Tipo mes** | INT64 | INT64 | ✅ **Igual** |

## Exemplo Prático: Consulta de Exportação

### Documentação Original (ERRADO para v_carga_metodologia_oficial)
```sql
-- INCORRETO para v_carga_metodologia_oficial
SELECT SUM(peso_carga) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
  AND sentido_carga = 'Exportação';  -- Valor não existe na view oficial
```

### Implementação Correta (ATUAL)
```sql
-- CORRETO para v_carga_metodologia_oficial
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024                    -- INT64, sem aspas
  AND isValidoMetodologiaANTAQ = 1  -- Filtro obrigatório
  AND sentido = 'Embarcados';        -- Exportação
```

## Validação com Dados Reais

| Porto | 2024 (Esperado) | v_carga_metodologia_oficial | Status |
|-------|-----------------|----------------------------|--------|
| Itaqui (MA) | ~34 milhões ton | 33.884.490 ton (`vlpesocargabruta_oficial`) | ✅ **Correto** |
| Santos (SP) | ~138 milhões ton | 138.692.300 ton (`vlpesocargabruta_oficial`) | ✅ **Correto** |

## Schema Completo da View Oficial

### v_carga_metodologia_oficial

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `idcarga` | STRING | ID da carga |
| `idatracacao` | STRING | ID da atracação |
| `cdmercadoria` | STRING | Código da mercadoria |
| `sentido` | STRING | 'Embarcados' (Export) ou 'Desembarcados' (Import) |
| `vlpesocargabruta_oficial` | FLOAT | **Peso bruto em toneladas - MÉTRICA PRINCIPAL** |
| `qtcarga_oficial` | FLOAT | Quantidade de carga |
| `teu` | STRING | TEU (container) |
| `origem` | STRING | Origem |
| `destino` | STRING | Destino |
| `porto_atracacao` | STRING | Nome do porto |
| `municipio` | STRING | Município |
| `uf` | STRING | Estado (UF) |
| `regiao_geografica` | STRING | Região geográfica |
| `tipo_de_navegacao_da_atracacao` | STRING | 'Longo Curso', 'Cabotagem', 'Interior' |
| `data_atracacao` | STRING | Data de atracação |
| `data_desatracacao` | STRING | Data de desatracação |
| `data_referencia` | DATE | Data de referência |
| `ano` | INT64 | Ano (2024, 2025, etc.) - **SEM aspas** |
| `mes` | INT64 | Mês (1-12) - **SEM aspas** |
| `tipo_operacao_da_carga` | STRING | Tipo de operação |
| `FlagAutorizacao` | STRING | Flag de autorização |
| `isValidoMetodologiaANTAQ` | INT64 | **Use = 1 para dados oficiais** |

## Ação Recomendada

**A implementação atual está correta.** A documentação original em `ai_agent_projeto/` precisa ser atualizada para refletir os nomes reais das colunas da view `v_carga_metodologia_oficial`.

### Arquivos que JÁ FORAM atualizados:
- ✅ `src/agent/prompts.py`
- ✅ `src/bigquery/vector_store.py`
- ✅ `config/prompts.yaml`
- ✅ `config/bigquery_config.yaml`
- ✅ `config/agent_config.yaml`
- ✅ `src/bigquery/schema.py`
- ✅ `SCHEMA.md`
- ✅ `README.md`

### Arquivos em ai_agent_projeto/ que precisam de nota:
- ⚠️ `02_schema_tabelas.md` - Baseado em tabelas brutas (ainda válido para tabelas)
- ⚠️ `03_dominio_negocio.md` - Contém nomes teóricos das colunas
- ⚠️ `04_views_consultaveis.md` - Menciona `v_carga_oficial_antaq` como principal
- ⚠️ `05_exemplos_perguntas_sql.md` - Exemplos usam `peso_carga` e `sentido_carga`

## Nota Importante

Os documentos em `ai_agent_projeto/` ainda são úteis como **referência do domínio de negócio**, mas os exemplos de SQL precisam ser ajustados para usar:
- View: `v_carga_metodologia_oficial`
- Métrica: `vlpesocargabruta_oficial`
- Filtro: `isValidoMetodologiaANTAQ = 1`
- Sentido: 'Embarcados'/'Desembarcados'
