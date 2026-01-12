# 03 - Domínio de Negócio ANTAQ

## Glossário e Conceitos

### Atracação

**Definição:** Ato de uma embarcação chegar ao porto e amarrar em um berço para realizar operações.

**Campos importantes:**
- `dt_atracacao`: Momento que o navio atracou
- `dt_desatracacao`: Momento que o navio saiu do berço
- `tempo_total_atracado`: Diferença entre desatracação e atracação (horas)
- `tempo_espera_atracacao`: Tempo de espera antes da atracação
- `tempo_operacao`: Tempo efetivo de operação com carga

**Tipos de operação:**
- **Carga:** Embarque de mercadorias (porto de origem)
- **Descarga:** Desembarque de mercadorias (porto de destino)
- **Embarque:** Passageiros
- **Desembarque:** Passageiros
- **Atracação sem operação:** Navio atracou mas não realizou operação

### Tipos de Navegação

| Tipo | Descrição | Exemplo |
|------|-----------|---------|
| **Longo Curso** | Comércio internacional | Navio da China para Brasil |
| **Cabotagem** | Transporte costeiro entre portos nacionais | Santos para Rio de Janeiro |
| **Interior** | Hidrovias interiores | Rio Madeira, Rio Paraná |

### Sentido da Carga

| Sentido | Descrição |
|---------|-----------|
| **Importação** | Carga entrando no país (Descarga de navio de longo curso) |
| **Exportação** | Carga saindo do país (Carga em navio de longo curso) |
| **Cabotagem** | Carga entre portos nacionais |

### Mercadorias

**Campos importantes:**
- `cd_mercadoria`: Código único da mercadoria
- `peso_carga`: Peso em toneladas
- `teu_movimentado`: TEU (Twenty-foot Equivalent Unit) para containers

**NCM (Nomenclatura Comum do Mercosul):**
- Sistema de classificação de mercadorias
- Usado para estatísticas de comércio exterior

### TEU (Twenty-foot Equivalent Unit)

**Definição:** Unidade equivalente a um container de 20 pés.

- 1 TEU = 1 container de 20 pés
- 1 container de 40 pés = 2 TEU
- Unidade padrão para medir capacidade de navios e portos

### Taxa de Ocupação

**Definição:** Percentual de tempo que um berço ficou ocupado.

```
Taxa de Ocupação = (Tempo Ocupado / Tempo Total) × 100
```

- `media_taxa_ocupacao`: Taxa média de ocupação do berço
- `media_taxa_ocupacao_com_carga`: Taxa considerando apenas períodos com operação

---

## Metodologia Oficial ANTAQ

### Flags de Validação

As tabelas possuem flags que determinam se uma operação deve ser contabilizada segundo a metodologia oficial:

| Flag | Valor Válido | Significado |
|------|--------------|-------------|
| `flagmcoperacaocarga` | '1' | Operação comercial válida |
| `flagoffshore` | NULL ou '0' | Excluir operações offshore |
| `FlagAutorizacao` | 'S' | Operação autorizada |

**Regra para Carga Oficial:**
```sql
WHERE flagmcoperacaocarga = '1'
  AND (flagoffshore IS NULL OR flagoffshore != '1')
  AND FlagAutorizacao = 'S'
```

### Data de Referência

**Regra importante:** A metodologia oficial ANTAQ usa a **data de desatracação** como referência para contabilização da carga.

Isso significa que uma carga é contabilizada no mês/ano em que o navio **saiu** do porto, não quando entrou.

---

## Regiões Geográficas

### Regiões do Brasil

- **Norte:** Amazonas, Pará, Rondônia, Roraima, Acre, Amapá, Tocantins
- **Nordeste:** Maranhão, Piauí, Ceará, Rio Grande do Norte, Paraíba, Pernambuco, Alagoas, Sergipe, Bahia
- **Sudeste:** Minas Gerais, Espírito Santo, Rio de Janeiro, São Paulo
- **Sul:** Paraná, Santa Catarina, Rio Grande do Sul
- **Centro-Oeste:** Mato Grosso, Mato Grosso do Sul, Goiás, Distrito Federal

### Regiões Hidrográficas

- **Amazônica:** Bacia Amazônica
- **Tocantins-Araguaia:** Bacia do Tocantins
- **Nordeste:** Bacias do Nordeste
- **São Francisco:** Rio São Francisco
- **Paraná:** Bacia do Paraná
- **Paraguai:** Rio Paraguai
- **Uruguai:** Rio Uruguai
- **Atlântico Leste:** Rios que desaguam no Atlântico
- **Sudeste:** Bacias do Sudeste

---

## Portos Principais

### Portos por Movimentação (2024)

| Porto | UF | Destaque |
|-------|-----|----------|
| Santos | SP | Maior porto do Brasil |
| Itaguaí | RJ | Minério de ferro |
| São Luís | MA | Minério de ferro |
| Rio Grande | RS | Grãos |
| Paranaguá | PR | Grãos e containers |
| Vitória | ES | Minério de ferro |

---

## Perguntas Comuns do Domínio

### Sobre Carga

| Pergunta | Tradução SQL |
|----------|--------------|
| Qual o total de carga movimentado? | SUM(peso_carga) |
| Qual a carga por tipo de navegação? | GROUP BY tipo_navegacao |
| Qual a carga por porto? | GROUP BY cd_porto, nm_porto |
| Qual a carga importada vs exportada? | GROUP BY sentido_carga |
| Qual a evolução mensal da carga? | GROUP BY ano, mes ORDER BY ano, mes |

### Sobre Atracação

| Pergunta | Tradução SQL |
|----------|--------------|
| Qual o número de atracações? | COUNT(id_atracacao) |
| Qual o tempo médio de atracação? | AVG(tempo_total_atracado) |
| Qual o tempo médio de espera? | AVG(tempo_espera_atracacao) |
| Qual a taxa de ocupação? | Usar tabela taxa_ocupacao |

### Sobre Containers

| Pergunta | Tradução SQL |
|----------|--------------|
| Quantos TEU foram movimentados? | SUM(teu_movimentado) |
| Quantos containers? | SUM(quantidade_conteineres) |

---

## Métricas Importantes

### Carga Total Oficial

```sql
SELECT
    ano,
    SUM(peso_carga) AS carga_total_toneladas
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
GROUP BY ano
ORDER BY ano;
```

### Carga por Tipo de Navegação

```sql
SELECT
    tipo_navegacao,
    SUM(peso_carga) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY tipo_navegacao;
```

### Carga Importada vs Exportada

```sql
SELECT
    sentido_carga,
    SUM(peso_carga) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY sentido_carga;
```

### Top Portos por Carga

```sql
SELECT
    nm_porto,
    uf,
    SUM(peso_carga) AS carga_total
FROM `antaqdados.br_antaq_estatistico_aquaviario.v_carga_oficial_antaq`
WHERE ano = 2024
GROUP BY nm_porto, uf
ORDER BY carga_total DESC
LIMIT 10;
```

---

## Contexto para o Agente AI

O agente deve ser configurado com as seguintes instruções de sistema:

```python
system_prompt = """
Você é um assistente especializado em analisar dados da ANTAQ (Agência Nacional de Transportes Aquaviários).

Regras importantes:
1. SEMPRE filtre por 'ano' quando possível para performance
2. Para métricas oficiais, use a view 'v_carga_oficial_antaq'
3. A carga oficia deve ter flagmcoperacaocarga = '1'
4. Exclua operações offshore (flagoffshore = '1')
5. Para consultas temporais, use dt_atracacao ou dt_desatracacao
6. Os pesos estão em toneladas; TEU é unidade de container
7. Tipos de navegação: 'Longo Curso', 'Cabotagem', 'Interior'
8. Sentidos de carga: 'Importação', 'Exportação', 'Cabotagem'

Sempre LIMIT os resultados a 1000 linhas por padrão.
"""
```
