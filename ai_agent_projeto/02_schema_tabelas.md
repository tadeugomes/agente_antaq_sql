# 02 - Esquema das Tabelas BigQuery

## Estrutura Completa das Tabelas

Dataset: `br_antaq_estatistico_aquaviario`

---

## Tabela: `atracacao`

**Descrição:** Operações de atracação de navios nos portos brasileiros.

**Chave Primária:** `id_atracacao`

| Coluna | Tipo | Descrição | Valores Comuns |
|--------|------|-----------|----------------|
| `ano` | INT64 | Ano da operação | 2000-2030 |
| `mes` | INT64 | Mês da operação | 1-12 |
| `id_atracacao` | STRING | Identificador único da atracação | UUID |
| `cd_porto` | STRING | Código do porto | BR**XX |
| `nm_porto` | STRING | Nome do porto | São Luís, Itaguaí, ... |
| `cd_berco` | STRING | Código do berco | Identificador |
| `dt_atracacao` | DATETIME | Data/hora de atracação | Timestamp |
| `dt_desatracacao` | DATETIME | Data/hora de desatracação | Timestamp |
| `dt_inicio_operacao` | DATETIME | Início da operação | Timestamp |
| `dt_fim_operacao` | DATETIME | Fim da operação | Timestamp |
| `tipo_operacao` | STRING | Tipo de operação | 'Carga', 'Descarga', 'Embarque', 'Desembarque' |
| `movimentacao_carga` | BOOLEAN | Indica se houve movimentação | true/false |
| `tempo_espera_atracacao` | FLOAT64 | Tempo de espera (horas) | Decimal |
| `tempo_inicio_operacao` | FLOAT64 | Tempo até início (horas) | Decimal |
| `tempo_operacao` | FLOAT64 | Tempo de operação (horas) | Decimal |
| `tempo_desatracacao` | FLOAT64 | Tempo de desatracação (horas) | Decimal |
| `tempo_total_atracado` | FLOAT64 | Tempo total atracado (horas) | Decimal |
| `tempo_estadia` | FLOAT64 | Tempo de estadia (horas) | Decimal |
| `tipo_navegacao` | STRING | Tipo de navegação | 'Longo Curso', 'Cabotagem', 'Interior' |
| `municipio` | STRING | Município do porto | Nome |
| `uf` | STRING | Unidade Federativa | Sigla UF |
| `regiao_geografica` | STRING | Região geográfica | 'Norte', 'Nordeste', ... |
| `regiao_hidrografica` | STRING | Região hidrográfica | Nome |

**SQL para obter schema:**
```sql
SELECT * FROM `antaqdados.br_antaq_estatistico_aquaviario.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'atracacao'
ORDER BY ordinal_position;
```

---

## Tabela: `carga`

**Descrição:** Movimentação de cargas (mercadorias) nos portos.

**Chave Primária:** `id_carga`
**Chave Estrangeira:** `id_atracacao` → `atracacao.id_atracacao`

| Coluna | Tipo | Descrição | Valores Comuns |
|--------|------|-----------|----------------|
| `ano` | INT64 | Ano da operação | 2000-2030 |
| `mes` | INT64 | Mês da operação | 1-12 |
| `id_carga` | STRING | Identificador único da carga | UUID |
| `id_atracacao` | STRING | FK para atracação | UUID |
| `cd_mercadoria` | STRING | Código da mercadoria | Código |
| `nm_mercadoria` | STRING | Nome da mercadoria | Descrição |
| `sg_mercadoria` | STRING | Sigla da mercadoria | Abreviação |
| `peso_carga` | FLOAT64 | Peso da carga em toneladas | Decimal (ton) |
| `tipo_navegacao` | STRING | Tipo de navegação | 'Longo Curso', 'Cabotagem', 'Interior' |
| `sentido_carga` | STRING | Sentido da operação | 'Importação', 'Exportação', 'Cabotagem' |
| `origem_destino` | STRING | Origem ou destino | Código instalação |
| `quantidade_conteineres` | INT64 | Número de containers | Inteiro |
| `teu_movimentado` | FLOAT64 | TEU (Twenty-foot Equivalent Unit) | Decimal |
| `tipo_conteiner` | STRING | Tipo de container | '20', '40', '45' |
| `terminal_origem` | STRING | Terminal de origem | Código |
| `terminal_destino` | STRING | Terminal de destino | Código |
| `flagmcoperacaocarga` | STRING | Flag operação comercial | '1' = comercial |
| `flagcabotagem` | STRING | Flag cabotagem | '1' = cabotagem |
| `flagoffshore` | STRING | Flag offshore | '1' = offshore |
| `flagtransporteviainterior` | STRING | Flag transporte via interior | '1' = interior |
| `tipo_operacao_da_carga` | STRING | Tipo da operação | 'Carga', 'Descarga', ... |

---

## Tabela: `instalacao_origem`

**Descrição:** Catálogo de instalações portuárias de origem.

**Chave Primária:** `origem`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `origem` | STRING | Código da instalação (PK) |
| `cd_tup_origem` | STRING | Código TUP |
| `nome` | STRING | Nome da instalação |
| `cidade` | STRING | Cidade |
| `uf` | STRING | UF |
| `pais` | STRING | País |
| `regiao_hidrografica` | STRING | Região hidrográfica |
| `bloco_economico` | STRING | Bloco econômico |

---

## Tabela: `instalacao_destino`

**Descrição:** Catálogo de instalações portuárias de destino.

**Chave Primária:** `destino`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `destino` | STRING | Código da instalação (PK) |
| `cd_tup_destino` | STRING | Código TUP |
| `nome` | STRING | Nome da instalação |
| `cidade` | STRING | Cidade |
| `uf` | STRING | UF |
| `pais` | STRING | País |
| `regiao_hidrografica` | STRING | Região hidrográfica |
| `bloco_economico` | STRING | Bloco econômico |

---

## Tabela: `mercadoria_carga`

**Descrição:** Catálogo de mercadorias transportadas.

**Chave Primária:** `cd_mercadoria`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cd_mercadoria` | STRING | Código da mercadoria (PK) |
| `ncm` | STRING | NCM - Nomenclatura Comum do Mercosul |
| `tipo_container` | STRING | Tipo de container |
| `grupo_mercadoria` | STRING | Grupo da mercadoria |
| `nomenclatura_simplificada` | STRING | Nomenclatura simplificada |

---

## Tabela: `mercadoria_carga_conteiner`

**Descrição:** Catálogo de mercadorias conteinerizadas.

**Chave Primária:** `cd_mercadoria_conteinerizada`

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `cd_mercadoria_conteinerizada` | STRING | Código da mercadoria conteinerizada (PK) |
| `cd_grupo_mercadoria_conteinerizada` | STRING | Código do grupo |
| `mercadoria_conteinerizada` | STRING | Nome da mercadoria |
| `nomenclatura_simplificada_conteinerizada` | STRING | Nomenclatura simplificada |

---

## Tabela: `taxa_ocupacao`

**Descrição:** Taxa de ocupação dos berços portuários.

**Chave Primária:** (`idberco`, `dia_taxa_ocupacao`)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `idberco` | STRING | ID do berço (FK) |
| `dia_taxa_ocupacao` | DATE | Dia da taxa |
| `min_taxa_ocupacao` | FLOAT64 | Taxa mínima (%) |
| `max_taxa_ocupacao` | FLOAT64 | Taxa máxima (%) |
| `media_taxa_ocupacao` | FLOAT64 | Taxa média (%) |
| `tempo_em_minutos` | INT64 | Tempo em minutos |
| `ano_taxa_ocupacao` | INT64 | Ano |

---

## Tabela: `taxa_ocupacao_com_carga`

**Descrição:** Taxa de ocupação com operação de carga.

**Chave Primária:** (`idberco`, `dia_taxa_ocupacao_com_carga`)

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `idberco` | STRING | ID do berço (FK) |
| `dia_taxa_ocupacao_com_carga` | DATE | Dia da taxa |
| `media_taxa_ocupacao_com_carga` | FLOAT64 | Taxa média com carga (%) |
| `tempo_em_minutos_dia` | INT64 | Tempo em minutos no dia |
| `ano_taxa_ocupacao_com_carga` | INT64 | Ano |

---

## Tabela: `tempos_atracacao`

**Descrição:** Tempos médios de atracação.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `idatracacao` | STRING | ID da atracação |
| `tesperaatracacao` | FLOAT64 | Tempo espera atracação |
| `toperacao` | FLOAT64 | Tempo de operação |
| `tesperadesatracacao` | FLOAT64 | Tempo espera desatracação |
| `tatracado` | FLOAT64 | Tempo total atracado |
| `testadia` | FLOAT64 | Tempo espera no dia |

---

## Relacionamentos (FK)

```
carga.id_atracacao → atracacao.id_atracacao
carga.origem_destino → instalacao_origem.origem (ou instalacao_destino.destino)
carga.cd_mercadoria → mercadoria_carga.cd_mercadoria
taxa_ocupacao.idberco → atracacao.cd_berco
```

---

## Schema JSON para o Agente AI

```json
{
  "dataset": "br_antaq_estatistico_aquaviario",
  "tables": [
    {
      "name": "atracacao",
      "description": "Operações de atracação de navios nos portos brasileiros",
      "primary_key": "id_atracacao",
      "columns": [
        {"name": "ano", "type": "INT64", "description": "Ano da operação"},
        {"name": "mes", "type": "INT64", "description": "Mês da operação"},
        {"name": "id_atracacao", "type": "STRING", "description": "Identificador único"},
        {"name": "cd_porto", "type": "STRING", "description": "Código do porto"},
        {"name": "nm_porto", "type": "STRING", "description": "Nome do porto"},
        {"name": "tipo_operacao", "type": "STRING", "description": "Tipo: Carga/Descarga/etc"},
        {"name": "tipo_navegacao", "type": "STRING", "description": "Longo Curso/Cabotagem/Interior"},
        {"name": "dt_atracacao", "type": "DATETIME", "description": "Data de atracação"},
        {"name": "dt_desatracacao", "type": "DATETIME", "description": "Data de desatracacao"},
        {"name": "tempo_total_atracado", "type": "FLOAT64", "description": "Tempo total atracado (horas)"}
      ]
    },
    {
      "name": "carga",
      "description": "Movimentação de cargas nos portos",
      "primary_key": "id_carga",
      "foreign_keys": [
        {"column": "id_atracacao", "references": "atracacao.id_atracacao"},
        {"column": "cd_mercadoria", "references": "mercadoria_carga.cd_mercadoria"}
      ],
      "columns": [
        {"name": "ano", "type": "INT64", "description": "Ano da operação"},
        {"name": "mes", "type": "INT64", "description": "Mês da operação"},
        {"name": "id_carga", "type": "STRING", "description": "Identificador único"},
        {"name": "id_atracacao", "type": "STRING", "description": "FK para atracacao"},
        {"name": "cd_mercadoria", "type": "STRING", "description": "Código da mercadoria"},
        {"name": "nm_mercadoria", "type": "STRING", "description": "Nome da mercadoria"},
        {"name": "peso_carga", "type": "FLOAT64", "description": "Peso em toneladas"},
        {"name": "sentido_carga", "type": "STRING", "description": "Importação/Exportação/Cabotagem"},
        {"name": "tipo_navegacao", "type": "STRING", "description": "Longo Curso/Cabotagem/Interior"},
        {"name": "teu_movimentado", "type": "FLOAT64", "description": "TEU movimentado"},
        {"name": "flagmcoperacaocarga", "type": "STRING", "description": "Flag operação comercial (1=válido)"}
      ]
    }
  ]
}
```
