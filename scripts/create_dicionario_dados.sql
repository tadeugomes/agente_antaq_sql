-- ============================================
-- Tabela: dicionario_dados
-- Dataset: br_antaq_estatistico_aquaviario
-- Project: antaqdados
--
-- Dicionário de dados centralizado para metadados
-- Usado pelo MetadataHelper para melhorar geração de SQL
-- ============================================

-- Criar tabela no dataset antaqdados (ou br_antaq_estatistico_aquaviario)
CREATE TABLE IF NOT EXISTS `antaqdados.br_antaq_estatistico_aquaviario.dicionario_dados`
(
    tabela STRING NOT NULL,              -- Nome da tabela/view
    coluna STRING NOT NULL,              -- Nome da coluna
    descricao STRING NOT NULL,           -- Descrição detalhada
    tipo_dado STRING NOT NULL,           -- Tipo de dado (STRING, INT64, FLOAT64, DATE, etc)
    valores_possiveis STRING,            -- Valores possíveis (se aplicável)
    categoria STRING NOT NULL,           -- Categoria (Identificação, Temporal, Métrica, Localização, etc)
    tags ARRAY<STRING>                   -- Tags para busca (ex: ['porto', 'exportação', 'métrica'])
)
CLUSTER BY tabela;

-- ============================================
-- Inserir dados das principais colunas da v_carga_metodologia_oficial
-- ============================================

INSERT INTO `antaqdados.br_antaq_estatistico_aquaviario.dicionario_dados`
(tabela, coluna, descricao, tipo_dado, valores_possiveis, categoria, tags)
VALUES
-- Identificação
('v_carga_metodologia_oficial', 'idcarga', 'Identificador único do registro de carga', 'STRING', NULL, 'Identificação', ['pk', 'carga', 'id']),
('v_carga_metodologia_oficial', 'idatracacao', 'Identificador da atracação relacionada', 'STRING', NULL, 'Identificação', ['fk', 'atracacao', 'id']),

-- Temporal
('v_carga_metodologia_oficial', 'ano', 'Ano da operação (formato INT64, usar sem aspas)', 'INT64', '2015-2025', 'Temporal', ['ano', 'periodo', 'filtro']),
('v_carga_metodologia_oficial', 'mes', 'Mês da operação (1-12)', 'INT64', '1-12', 'Temporal', ['mês', 'periodo', 'filtro']),
('v_carga_metodologia_oficial', 'data_referencia', 'Data de referência para cálculos oficiais', 'DATE', NULL, 'Temporal', ['data', 'referência']),
('v_carga_metodologia_oficial', 'data_atracacao', 'Data da atracação da embarcação', 'TIMESTAMP', NULL, 'Temporal', ['data', 'atracacao']),

-- Localização
('v_carga_metodologia_oficial', 'porto_atracacao', 'Nome do porto onde ocorreu a atracação', 'STRING', NULL, 'Localização', ['porto', 'local', 'uf', 'estado']),
('v_carga_metodologia_oficial', 'uf', 'Unidade Federativa (estado) do porto', 'STRING', 'SP, RJ, ES, etc', 'Localização', ['uf', 'estado', 'região']),
('v_carga_metodologia_oficial', 'regiao_geografica', 'Região geográfica do porto', 'STRING', NULL, 'Localização', ['região', 'geografia']),

-- Mercadoria
('v_carga_metodologia_oficial', 'cdmercadoria', 'Código da mercadoria segundo classificação ANTAQ', 'STRING', NULL, 'Mercadoria', ['mercadoria', 'produto', 'código']),
('v_carga_metodologia_oficial', 'natureza_carga', 'Natureza da carga (carga geral, granel sólido, granel líquido, etc)', 'STRING', NULL, 'Mercadoria', ['natureza', 'tipo', 'classificação']),

-- Operação
('v_carga_metodologia_oficial', 'sentido', 'Direção do fluxo da carga', 'STRING', 'Embarcados (exportação), Desembarcados (importação)', 'Operação', ['sentido', 'direção', 'exportação', 'importação']),
('v_carga_metodologia_oficial', 'tipo_de_navegacao_da_atracacao', 'Tipo de navegação da embarcação', 'STRING', 'Longo Curso, Cabotagem, Interior', 'Operação', ['navegação', 'tipo', 'classificação']),
('v_carga_metodologia_oficial', 'tipo_operacao_da_carga', 'Tipo da operação de carga', 'STRING', NULL, 'Operação', ['operação', 'tipo', 'atividade']),

-- Métricas
('v_carga_metodologia_oficial', 'vlpesocargabruta_oficial', 'Peso bruto da carga em toneladas (métrica oficial ANTAQ)', 'FLOAT64', NULL, 'Métrica', ['peso', 'tonelada', 'volume', 'métrica principal', 'oficial']),
('v_carga_metodologia_oficial', 'qtcarga_oficial', 'Quantidade da carga segundo unidade de medida', 'FLOAT64', NULL, 'Métrica', ['quantidade', 'unidade']),
('v_carga_metodologia_oficial', 'teu', 'Número de contêineres em TEU (Twenty-foot Equivalent Unit)', 'FLOAT64', NULL, 'Métrica', ['teu', 'contêiner', 'unidade']),

-- Validação
('v_carga_metodologia_oficial', 'isValidoMetodologiaANTAQ', 'Flag indicando se o registro é válido pela metodologia oficial ANTAQ (usar = 1 para dados oficiais)', 'INT64', '0 ou 1', 'Validação', ['validação', 'oficial', 'filtro', 'metodologia']),
('v_carga_metodologia_oficial', 'FlagAutorizacao', 'Flag de autorização da operação (S = autorizado)', 'STRING', 'S, N', 'Validação', ['autorização', 'validação'])

-- Obs: Adicionar mais colunas conforme necessário
-- Para bulk insert, usar CSV ou executar múltiplos INSERT VALUES
;

-- ============================================
-- Criar índices para busca eficiente
-- ============================================

-- Não é possível criar índices tradicionais no BigQuery,
-- mas a tabela está clusterizada por tabela para melhor performance

-- ============================================
-- Exemplos de queries usando o dicionário_dados
-- ============================================

-- Buscar colunas por palavra-chave
/*
SELECT tabela, coluna, descricao, tipo_dado, categoria
FROM `antaqdados.br_antaq_estatistico_aquaviario.dicionario_dados`
WHERE LOWER(descricao) LIKE '%peso%'
   OR EXISTS (SELECT 1 FROM UNNEST(tags) AS tag WHERE LOWER(tag) = 'peso')
ORDER BY tabela, categoria, coluna;
*/

-- Buscar todas as colunas de uma tabela
/*
SELECT coluna, descricao, tipo_dado, categoria
FROM `antaqdados.br_antaq_estatistico_aquaviario.dicionario_dados`
WHERE tabela = 'v_carga_metodologia_oficial'
ORDER BY categoria, coluna;
*/

-- Buscar colunas por categoria
/*
SELECT tabela, coluna, descricao
FROM `antaqdados.br_antaq_estatistico_aquaviario.dicionario_dados`
WHERE categoria = 'Métrica'
ORDER BY tabela, coluna;
*/
