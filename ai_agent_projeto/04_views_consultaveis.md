# 04 - Views Consultáveis

## Views Disponíveis no BigQuery

**Importante:** Para o agente AI, recomenda-se usar as **views validadas** em vez das tabelas brutas, pois já incluem validações de integridade referencial e regras de negócio.

---

## View: `v_carga_oficial_antaq`

**Descrição:** View que implementa a metodologia oficial ANTAQ para contabilização de carga.

**Regras aplicadas:**
- `flagmcoperacaocarga = '1'` (apenas operações comerciais)
- Exclui operações offshore (`flagoffshore != '1'`)
- Usa `FlagAutorizacao = 'S'`

**Campos:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ano` | INT64 | Ano de referência (baseado em desatracação) |
| `mes` | INT64 | Mês de referência (baseado em desatracação) |
| `id_carga` | STRING | ID da carga |
| `id_atracacao` | STRING | ID da atracacao |
| `cd_porto` | STRING | Código do porto |
| `nm_porto` | STRING | Nome do porto |
| `uf` | STRING | UF do porto |
| `cd_mercadoria` | STRING | Código da mercadoria |
| `nm_mercadoria` | STRING | Nome da mercadoria |
| `peso_carga` | FLOAT64 | Peso em toneladas |
| `sentido_carga` | STRING | Importação/Exportação/Cabotagem |
| `tipo_navegacao` | STRING | Longo Curso/Cabotagem/Interior |
| `tipo_operacao_da_carga` | STRING | Carga/Descarga/etc |

**Exemplo de consulta:**
```sql
SELECT
    ano,
    mes,
    nm_porto,
    SUM(peso_carga) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY ano, mes, nm_porto
ORDER BY mes, carga_total DESC;
```

---

## View: `v_carga_metodologia_oficial`

**Descrição:** View alinhada com a metodologia oficial ANTAQ.

**Regras aplicadas:**
- `FlagAutorizacao = 'S'`
- Referência por data de desatracação
- Inclui todos os tipos de operação oficiais

**Campos:** Similar à `v_carga_oficial_antaq`

---

## View: `v_atracacao_validada`

**Descrição:** Atracação com validação de chaves estrangeiras.

**Validações:**
- Verifica existência de porto
- Verifica consistência de datas
- Exclui registros com FK inválida

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_atracacao` | STRING | ID da atracação |
| `ano` | INT64 | Ano da operação |
| `mes` | INT64 | Mês da operação |
| `cd_porto` | STRING | Código do porto |
| `nm_porto` | STRING | Nome do porto |
| `dt_atracacao` | DATETIME | Data de atracação |
| `dt_desatracacao` | DATETIME | Data de desatracação |
| `tempo_total_atracado` | FLOAT64 | Tempo total atracado |
| `tipo_operacao` | STRING | Tipo de operação |
| `tipo_navegacao` | STRING | Tipo de navegação |
| `uf` | STRING | UF |

**Exemplo de consulta:**
```sql
SELECT
    nm_porto,
    COUNT(*) AS qt_atracacoes,
    AVG(tempo_total_atracado) AS tempo_medio_horas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_atracacao_validada`
WHERE ano = 2024
GROUP BY nm_porto
ORDER BY qt_atracacoes DESC;
```

---

## View: `v_carga_validada`

**Descrição:** Carga com validação de relacionamentos.

**Validações:**
- Verifica existência de atracacao relacionada
- Verifica existência de mercadoria
- Exclui registros sem relacionamento válido

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `id_carga` | STRING | ID da carga |
| `id_atracacao` | STRING | ID da atracacao |
| `cd_mercadoria` | STRING | Código da mercadoria |
| `nm_mercadoria` | STRING | Nome da mercadoria |
| `peso_carga` | FLOAT64 | Peso em toneladas |
| `sentido_carga` | STRING | Sentido da operação |
| `ano` | INT64 | Ano |
| `mes` | INT64 | Mês |

---

## View: `v_tempos_atracacao_validada`

**Descrição:** Tempos de atracacao com validação de intervalos.

**Validações:**
- Verifica se tempos são não-negativos
- Verifica se desatracacao > atracacao
- Exclui registros com tempos inválidos

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `idatracacao` | STRING | ID da atracação |
| `tesperaatracacao` | FLOAT64 | Tempo espera atracação |
| `toperacao` | FLOAT64 | Tempo operação |
| `tatracado` | FLOAT64 | Tempo total atracado |
| `testadia` | FLOAT64 | Tempo espera no dia |

---

## View: `v_resumo_integridade_referencial`

**Descrição:** Resumo da qualidade dos dados e integridade referencial.

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `tabela` | STRING | Nome da tabela |
| `total_registros` | INT64 | Total de registros |
| `registros_validos` | INT64 | Registros válidos |
| `registros_invalidos` | INT64 | Registros com problemas |
| `percentual_valido` | FLOAT64 | % de registros válidos |

**Uso:** Monitoramento da qualidade dos dados

```sql
SELECT *
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_resumo_integridade_referencial`
ORDER BY percentual_valido DESC;
```

---

## View: `v_analise_portuaria_1semestre_2025`

**Descrição:** View de análise portuária validada contra dados oficiais ANTAQ.

**Validação:** Total de 655.6 milhões de toneladas (1º semestre 2025)

**Campos principais:**

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `ano` | INT64 | Ano |
| `mes` | INT64 | Mês |
| `tipo_navegacao` | STRING | Tipo de navegação |
| `sentido_carga` | STRING | Sentido da carga |
| `nm_porto` | STRING | Nome do porto |
| `carga_total` | FLOAT64 | Total da carga (ton) |
| `variacao_mensal` | FLOAT64 | Variação sobre mês anterior (%) |

---

## Recomendações para o Agente AI

### Views Prioritárias

Use estas views em ordem de prioridade:

1. **`v_carga_oficial_antaq`** - Para métricas oficiais de carga
2. **`v_atracacao_validada`** - Para análise de atracação
3. **`v_carga_validada`** - Para análise detalhada de carga

### Regras para o Agente

```python
# System prompt específico para views
view_instructions = """
Para consultas de carga e movimentação, use estas views:

1. v_carga_oficial_antaq - Para totais oficiais (recomendado)
   - Aplica filtros de metodologia ANTAQ automaticamente
   - Use para: totais anuais, mensais, por porto, por tipo de navegação

2. v_atracacao_validada - Para análise de atracação
   - Use para: número de atracações, tempos médios, taxa de ocupação

3. v_carga_validada - Para análise detalhada de carga
   - Use quando precisa de detalhes não disponíveis na view oficial

IMPORTANTE: Sempre prefira views validadas sobre tabelas brutas.
"""
```

### Exemplo de Schema para LangChain

```python
# Configurar LangChain para usar views
from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri(
    "bigquery://antaqdados/br_antaq_estatistico_aquaviario",
    include_tables=[
        "v_carga_oficial_antaq",
        "v_atracacao_validada",
        "v_carga_validada",
        "instalacao_origem",
        "instalacao_destino",
        "mercadoria_carga"
    ],
    sample_rows_in_table_info=3
)
```
