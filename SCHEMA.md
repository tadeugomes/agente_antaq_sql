# ANTAQ BigQuery Schema Reference

## CRITICAL: Primary Table for Official Cargo Metrics

**Table:** `v_carga_metodologia_oficial`
**Dataset:** `antaqdados.br_antaq_estatistico_aquaviario`

This view applies ANTAQ's official methodology for cargo statistics.

### Required Filters (ALWAYS use these)

```sql
WHERE ano = 2024              -- Year is INT64, no quotes
  AND isValidoMetodologiaANTAQ = 1  -- Official methodology validation
```

### Key Columns

| Column | Type | Description |
|--------|------|-------------|
| `ano` | INT64 | Year (e.g., 2024) - **ALWAYS filter by this** |
| `mes` | INT64 | Month (1-12) - **Integer, not string** |
| `porto_atracacao` | STRING | Port name |
| `uf` | STRING | State code |
| **`vlpesocargabruta_oficial`** | FLOAT | **Gross cargo weight in tons - PRIMARY METRIC** |
| `qtcarga_oficial` | FLOAT | Cargo quantity |
| `sentido` | STRING | 'Embarcados' (Export) or 'Desembarcados' (Import) |
| `tipo_de_navegacao_da_atracacao` | STRING | Navigation type |
| `cdmercadoria` | STRING | Commodity code |
| `isValidoMetodologiaANTAQ` | INT64 | Validation flag (use = 1) |

### Navigation Types (tipo_de_navegacao_da_atracacao)

- `'Longo Curso'` - International maritime transport
- `'Cabotagem'` - Domestic coastal transport
- `'Interior'` - Inland waterways transport

### Load Directions (sentido)

**IMPORTANT:** In `v_carga_metodologia_oficial`, the values are:
- `'Embarcados'` - Export (cargo leaving Brazil)
- `'Desembarcados'` - Import (cargo entering Brazil)

## Example Queries

### Total cargo by year
```sql
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
```

### Cargo by port (top 10)
```sql
SELECT porto_atracacao, uf,
       SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
GROUP BY porto_atracacao, uf
ORDER BY carga_total DESC
LIMIT 10
```

### Specific port (case-insensitive)
```sql
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
  AND LOWER(porto_atracacao) LIKE '%itaqui%'
```

### Cargo by navigation type
```sql
SELECT tipo_de_navegacao_da_atracacao,
       SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
GROUP BY tipo_de_navegacao_da_atracacao
ORDER BY carga_total DESC
```

### Export only (Embarcados)
```sql
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
  AND sentido = 'Embarcados'  -- Export
```

### Import only (Desembarcados)
```sql
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
  AND sentido = 'Desembarcados'  -- Import
```

### Import vs Export comparison
```sql
SELECT sentido,
       SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
GROUP BY sentido
ORDER BY carga_total DESC
```

### Export by port and month (e.g., Santos January 2025)
```sql
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2025
  AND mes = 1
  AND isValidoMetodologiaANTAQ = 1
  AND LOWER(porto_atracacao) LIKE '%santos%'
  AND sentido = 'Embarcados'  -- Export
```

## Other Available Views

| View | Purpose |
|------|---------|
| `v_atracacao_validada` | Docking/berthing analysis |
| `v_carga_validada` | Validated cargo data (different methodology) |
| `v_resumo_instalacoes` | Port installation summary |
| `v_resumo_mercadorias` | Commodity summary |

## Common Pitfalls to Avoid

### Wrong: Using STRING for year
```sql
-- DON'T: ano = '2024' (wrong data type)
WHERE ano = '2024'
```

### Right: Using INT64 for year
```sql
-- DO: ano = 2024 (correct data type)
WHERE ano = 2024
```

### Wrong: Using wrong view/metric
```sql
-- DON'T: Wrong view and metric
SELECT SUM(qtcarga_numeric) ...
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
```

### Right: Using official view
```sql
-- DO: Official view and metric
SELECT SUM(vlpesocargabruta_oficial) ...
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE isValidoMetodologiaANTAQ = 1
```

### Wrong: Forgetting official methodology filter
```sql
-- DON'T: Missing validation filter
WHERE ano = 2024
```

### Right: Including official methodology filter
```sql
-- DO: Always include validation filter
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
```

### Wrong: Case-sensitive port matching
```sql
-- DON'T: Will miss "ITAQUI", "Itaqui", etc.
WHERE porto_atracacao = 'Itaqui'
```

### Right: Case-insensitive port matching
```sql
-- DO: Will match any case variation
WHERE LOWER(porto_atracacao) LIKE '%itaqui%'
```

## Data Type Reference

| Concept | Data Type | Example |
|---------|-----------|---------|
| Year | INT64 | `2024` (no quotes) |
| Month | INT64 | `1` (no quotes) |
| Port Name | STRING | `'Itaqui'` (quotes) |
| State | STRING | `'MA'` (quotes) |
| Weight | FLOAT | `33884490.0` |

## Metric Comparison

| Metric | View | Purpose |
|--------|------|---------|
| `vlpesocargabruta_oficial` | `v_carga_metodologia_oficial` | **Official gross weight (tons)** |
| `qtcarga_oficial` | `v_carga_metodologia_oficial` | Official cargo quantity |
| `vlpesocargabruta_numeric` | `v_carga_oficial_antaq` | Alternative view (less accurate) |
| `qtcarga_numeric` | `v_carga_oficial_antaq` | Alternative view (less accurate) |

**IMPORTANT:** Always use `v_carga_metodologia_oficial` with `vlpesocargabruta_oficial` for official statistics.
