# ATUALIZAÇÕES - Implementação Real vs Documentação Original

## Data: 2025-12-31

## Motivo

Este documento registra as diferenças encontradas entre a documentação original e a realidade do BigQuery, após validação com dados reais.

## Views Disponíveis - Atualização

### Prioridade de Uso (Atualizado)

| Ordem | View | Uso | Status |
|-------|------|-----|--------|
| 1 | `v_carga_metodologia_oficial` | **Métricas oficiais ANTAQ** | ✅ **PRINCIPAL** |
| 2 | `v_carga_oficial_antaq` | Carga com flags básicas | ⚠️ Secundário |
| 3 | `v_atracacao_validada` | Análise de atracação | ✅ Para tempos |
| 4 | `v_carga_validada` | Carga com relacionamentos | ✅ Para detalhes |

## Schema Atualizado - v_carga_metodologia_oficial

### Diferenças Principais vs Documentação Original

| Documentação Original | View Real | Observação |
|----------------------|-----------|------------|
| `peso_carga` | `vlpesocargabruta_oficial` | Nome da coluna diferente |
| `sentido_carga` | `sentido` | Nome da coluna diferente |
| 'Importação'/'Exportação' | 'Embarcados'/'Desembarcados' | **Valores diferentes** |
| `nm_porto` | `porto_atracacao` | Nome da coluna diferente |
| `tipo_navegacao` | `tipo_de_navegacao_da_atracacao` | Nome da coluna diferente |

### Schema Completo (v_carga_metodologia_oficial)

```
Colunas Principais:
- idcarga (STRING) - ID da carga
- idatracacao (STRING) - ID da atracação
- cdmercadoria (STRING) - Código da mercadoria
- sentido (STRING) - 'Embarcados' ou 'Desembarcados'
- vlpesocargabruta_oficial (FLOAT) - Peso bruto em toneladas [MÉTRICA PRINCIPAL]
- qtcarga_oficial (FLOAT) - Quantidade de carga
- porto_atracacao (STRING) - Nome do porto
- uf (STRING) - Estado
- tipo_de_navegacao_da_atracacao (STRING) - Tipo de navegação
- ano (INT64) - Ano [SEM aspas na query]
- mes (INT64) - Mês [SEM aspas na query]
- isValidoMetodologiaANTAQ (INT64) - Filtro [= 1 para dados oficiais]
```

## Exemplos SQL Atualizados

### Total de Carga 2024

```sql
-- CORRETO
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024                    -- INT64, sem aspas
  AND isValidoMetodologiaANTAQ = 1;
```

### Exportação vs Importação

```sql
-- CORRETO
SELECT sentido, SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2024
  AND isValidoMetodologiaANTAQ = 1
GROUP BY sentido;
-- Retorna: 'Embarcados' (Exportação) e 'Desembarcados' (Importação)
```

### Porto Específico

```sql
-- CORRETO - Santos Janeiro 2025
SELECT SUM(vlpesocargabruta_oficial) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_metodologia_oficial`
WHERE ano = 2025
  AND mes = 1
  AND isValidoMetodologiaANTAQ = 1
  AND LOWER(porto_atracacao) LIKE '%santos%'
  AND sentido = 'Embarcados';  -- Exportação
```

## Validação com Dados Reais

| Porto | Ano | Resultado (vlpesocargabruta_oficial) | Validação |
|-------|-----|-------------------------------------|-----------|
| Itaqui (MA) | 2024 | 33.884.490 ton | ✅ Confere com dados oficiais |
| Santos (SP) | 2024 | 138.692.300 ton | ✅ Confere com dados oficiais |
| Santos Jan 2025 | 2025 | 6.861.905 ton (Export) | ✅ Dados disponíveis |

## Sistema Prompt Atualizado

```python
SYSTEM_PROMPT = """
You are an expert data analyst for ANTAQ.

**CRITICAL: Use v_carga_metodologia_oficial for official metrics**

Core Columns:
- ano (INT64) - Use 2024 (no quotes)
- mes (INT64) - Use 1-12 (no quotes)
- porto_atracacao (STRING) - Port name
- vlpesocargabruta_oficial (FLOAT) - Gross weight in tons [PRIMARY METRIC]
- sentido (STRING) - 'Embarcados' (Export) or 'Desembarcados' (Import)
- isValidoMetodologiaANTAQ (INT64) - Always filter = 1

Rules:
1. ALWAYS filter: ano = 2024 (INT64, no quotes)
2. ALWAYS filter: isValidoMetodologiaANTAQ = 1
3. Use vlpesocargabruta_oficial for cargo weight
4. Use LOWER(porto_atracacao) LIKE '%santos%' for ports
5. For export: sentido = 'Embarcados'
6. For import: sentido = 'Desembarcados'
"""
```

## Conclusão

A implementação atual do projeto está **CORRETA** e usa a view e colunas apropriadas do BigQuery. Este documento serve como referência para atualizações futuras da documentação original.
