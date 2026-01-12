# 05 - Exemplos de Perguntas-SQL

## Pares Pergunta → SQL para Treinamento do Agente

Esta seção contém exemplos de perguntas em linguagem natural e suas correspondentes queries SQL. Use estes exemplos para few-shot learning e RAG.

---

## Perguntas Básicas

### P1: Total de carga movimentado

**Pergunta:** Qual foi o total de carga movimentado em 2024?

```sql
SELECT
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024;
```

**Resultado esperado:** ~655 milhões de toneladas (1º sem) ou ~1.3 bilhão (ano completo)

---

### P2: Carga por tipo de navegação

**Pergunta:** Qual a carga movimentada por tipo de navegação em 2024?

```sql
SELECT
    tipo_navegacao,
    SUM(peso_carga) AS carga_total_toneladas,
    ROUND(SUM(peso_carga) / SUM(SUM(peso_carga)) OVER () * 100, 2) AS percentual
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY tipo_navegacao
ORDER BY carga_total_toneladas DESC;
```

---

### P3: Carga importada vs exportada

**Pergunta:** Quanto foi importado e quanto foi exportado em 2024?

```sql
SELECT
    sentido_carga,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY sentido_carga
ORDER BY carga_total_toneladas DESC;
```

---

### P4: Top portos por carga

**Pergunta:** Quais são os 10 maiores portos por movimentação de carga em 2024?

```sql
SELECT
    nm_porto,
    uf,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY nm_porto, uf
ORDER BY carga_total_toneladas DESC
LIMIT 10;
```

---

### P5: Carga mensal (série temporal)

**Pergunta:** Qual foi a evolução mensal da carga em 2024?

```sql
SELECT
    mes,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY mes
ORDER BY mes;
```

---

### P6: Carga por região geográfica

**Pergunta:** Qual a carga por região geográfica em 2024?

```sql
SELECT
    regiao_geografica,
    SUM(peso_carga) AS carga_total_toneladas
FROM (
    SELECT
        c.peso_carga,
        a.regiao_geografica
    FROM `antaqdados.br_antaq_estatistico_aquaviario.carga` c
    INNER JOIN `antaqdados.br_antaq_estatistico_aquaviario.atracacao` a
        ON c.id_atracacao = a.id_atracacao
    WHERE c.ano = 2024
        AND c.flagmcoperacaocarga = '1'
) x
GROUP BY regiao_geografica
ORDER BY carga_total_toneladas DESC;
```

---

### P7: Número de atracações

**Pergunta:** Quantas atracações houveram em 2024?

```sql
SELECT
    COUNT(*) AS total_atracacoes,
    COUNT(DISTINCT cd_porto) AS portos_atracados
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_atracacao_validada`
WHERE ano = 2024;
```

---

### P8: Tempo médio de atracação

**Pergunta:** Qual o tempo médio de atracação por porto em 2024?

```sql
SELECT
    nm_porto,
    uf,
    COUNT(*) AS qt_atracacoes,
    ROUND(AVG(tempo_total_atracado), 2) AS tempo_medio_horas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_atracacao_validada`
WHERE ano = 2024
    AND tempo_total_atracado IS NOT NULL
    AND tempo_total_atracado > 0
GROUP BY nm_porto, uf
HAVING COUNT(*) >= 10
ORDER BY tempo_medio_horas DESC;
```

---

### P9: Carga por mercadoria (top 10)

**Pergunta:** Quais são as 10 principais mercadorias movimentadas em 2024?

```sql
SELECT
    nm_mercadoria,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
    AND nm_mercadoria IS NOT NULL
GROUP BY nm_mercadoria
ORDER BY carga_total_toneladas DESC
LIMIT 10;
```

---

### P10: TEU movimentado

**Pergunta:** Quantos TEU foram movimentados em 2024?

```sql
SELECT
    SUM(teu_movimentado) AS teu_total,
    SUM(quantidade_conteineres) AS qt_containers
FROM `antaqdados.br_antaq_estatistico_aquaviario.carga`
WHERE ano = 2024
    AND teu_movimentado IS NOT NULL;
```

---

## Perguntas Comparativas

### P11: Comparação ano a ano

**Pergunta:** Comparar a carga de 2023 com 2024

```sql
WITH carga_anual AS (
    SELECT
        ano,
        SUM(peso_carga) AS carga_total
    FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
    WHERE ano IN (2023, 2024)
    GROUP BY ano
)
SELECT
    ano,
    carga_total,
    LAG(carga_total) OVER (ORDER BY ano) AS ano_anterior,
    ROUND((carga_total - LAG(carga_total) OVER (ORDER BY ano)) /
          LAG(carga_total) OVER (ORDER BY ano) * 100, 2) AS variacao_percentual
FROM carga_anual
ORDER BY ano;
```

---

### P12: Comparação por porto

**Pergunta:** Qual a variação da carga no porto de Santos entre 2023 e 2024?

```sql
WITH carga_porto AS (
    SELECT
        ano,
        nm_porto,
        SUM(peso_carga) AS carga_total
    FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
    WHERE ano IN (2023, 2024)
        AND nm_porto LIKE '%Santos%'
    GROUP BY ano, nm_porto
)
SELECT
    nm_porto,
    MAX(CASE WHEN ano = 2023 THEN carga_total END) AS carga_2023,
    MAX(CASE WHEN ano = 2024 THEN carga_total END) AS carga_2024,
    ROUND((MAX(CASE WHEN ano = 2024 THEN carga_total END) -
           MAX(CASE WHEN ano = 2023 THEN carga_total END)) /
           MAX(CASE WHEN ano = 2023 THEN carga_total END) * 100, 2) AS variacao_percentual
FROM carga_porto
GROUP BY nm_porto;
```

---

## Perguntas Complexas

### P13: Ranking de portos por tipo de navegação

**Pergunta:** Quais os principais portos de cabotagem em 2024?

```sql
SELECT
    nm_porto,
    uf,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
    AND tipo_navegacao = 'Cabotagem'
GROUP BY nm_porto, uf
ORDER BY carga_total_toneladas DESC
LIMIT 10;
```

---

### P14: Carga de um porto específico

**Pergunta:** Qual a movimentação do porto de São Luís em 2024?

```sql
SELECT
    sentido_carga,
    tipo_navegacao,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
    AND nm_porto LIKE '%São Luís%'
GROUP BY sentido_carga, tipo_navegacao
ORDER BY carga_total_toneladas DESC;
```

---

### P15: Carga por estado (UF)

**Pergunta:** Qual a carga por estado em 2024?

```sql
SELECT
    uf,
    SUM(peso_carga) AS carga_total_toneladas,
    ROUND(SUM(peso_carga) / SUM(SUM(peso_carga)) OVER () * 100, 2) AS percentual
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY uf
ORDER BY carga_total_toneladas DESC;
```

---

### P16: Mercadorias de um porto específico

**Pergunta:** Quais mercadorias são mais movimentadas no porto de Santos?

```sql
SELECT
    nm_mercadoria,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE nm_porto LIKE '%Santos%'
    AND ano = 2024
GROUP BY nm_mercadoria
ORDER BY carga_total_toneladas DESC
LIMIT 10;
```

---

### P17: Análise de origem/destino

**Pergunta:** Quais países são os principais parceiros (importação) em 2024?

```sql
SELECT
    i.pais AS pais_origem,
    SUM(c.peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.carga` c
INNER JOIN `antaqdados.br_antaq_estatistico_aquaviario.instalacao_origem` i
    ON c.origem_destino = i.origem
WHERE c.ano = 2024
    AND c.sentido_carga = 'Importação'
    AND c.flagmcoperacaocarga = '1'
GROUP BY i.pais
ORDER BY carga_total_toneladas DESC
LIMIT 10;
```

---

### P18: Concentração de mercado (HHI)

**Pergunta:** Qual a concentração de carga nos top 5 portos?

```sql
WITH ranking_portos AS (
    SELECT
        nm_porto,
        SUM(peso_carga) AS carga_total,
        ROW_NUMBER() OVER (ORDER BY SUM(peso_carga) DESC) AS ranking
    FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
    WHERE ano = 2024
    GROUP BY nm_porto
),
total_ano AS (
    SELECT SUM(peso_carga) AS total
    FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
    WHERE ano = 2024
)
SELECT
    r.nm_porto,
    r.carga_total,
    ROUND(r.carga_total / t.total * 100, 2) AS percentual,
    SUM(r.carga_total) OVER (ORDER BY r.carga_total DESC) / t.total * 100 AS acumulado_percentual
FROM ranking_portos r
CROSS JOIN total_ano t
WHERE r.ranking <= 5
ORDER BY r.carga_total DESC;
```

---

## Exemplos para RAG (Vector Store)

### Formato JSON para BigQuery Vector Store

```json
{
  "table": "qa_examples",
  "rows": [
    {
      "question": "Qual foi o total de carga movimentado em 2024?",
      "sql": "SELECT SUM(peso_carga) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024",
      "category": "total_geral",
      "difficulty": "basico"
    },
    {
      "question": "Quais são os 10 maiores portos por movimentação?",
      "sql": "SELECT nm_porto, uf, SUM(peso_carga) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY nm_porto, uf ORDER BY carga_total DESC LIMIT 10",
      "category": "ranking",
      "difficulty": "basico"
    },
    {
      "question": "Compare a carga de importação com exportação",
      "sql": "SELECT sentido_carga, SUM(peso_carga) AS carga_total FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY sentido_carga",
      "category": "comparacao",
      "difficulty": "basico"
    }
  ]
}
```

### Tabela para Armazenar Exemplos

```sql
-- Tabela de exemplos para RAG
CREATE TABLE `antaqdados.br_antaq_estatistico_aquaviario.qa_examples` (
  example_id STRING PRIMARY KEY,
  question STRING NOT NULL,
  sql_query STRING NOT NULL,
  category STRING,
  difficulty STRING,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP()
);

-- Tabela de embeddings (usar BigQuery Vector Search)
CREATE TABLE `antaqdados.br_antaq_estatistico_aquaviario.qa_embeddings` (
  example_id STRING,
  question_embedding ARRAY<FLOAT64>,
  FOREIGN KEY (example_id) REFERENCES qa_examples(example_id)
);
```

---

## Categorias de Perguntas

| Categoria | Descrição | Perguntas |
|-----------|-----------|-----------|
| `total_geral` | Totais agregados | P1, P7, P10 |
| `por_navegacao` | Por tipo de navegação | P2, P13 |
| `por_porto` | Por porto específico | P4, P14, P16 |
| `por_sentido` | Importação/Exportação | P3, P17 |
| `serie_temporal` | Evolução temporal | P5, P11, P12 |
| `por_mercadoria` | Por tipo de carga | P9, P16 |
| `analise_complexa` | Análises avançadas | P6, P18 |

---

## Dicas para Few-Shot Learning

Ao configurar o agente, forneça de 3-5 exemplos representativos no prompt:

```python
few_shot_examples = """
Exemplo 1:
Pergunta: Qual o total de carga em 2024?
SQL: SELECT SUM(peso_carga) FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024

Exemplo 2:
Pergunta: Top 5 portos por carga?
SQL: SELECT nm_porto, SUM(peso_carga) FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY nm_porto ORDER BY SUM(peso_carga) DESC LIMIT 5

Exemplo 3:
Pergunta: Carga de importação vs exportação?
SQL: SELECT sentido_carga, SUM(peso_carga) FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq` WHERE ano = 2024 GROUP BY sentido_carga
"""
```
