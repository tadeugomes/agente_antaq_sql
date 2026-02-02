"""
Helper functions for querying referential data tables
Used to enrich query results with friendly names from reference tables
"""
import os
import re
from typing import Optional, Dict, Any
import pandas as pd


# Mapeamento manual de portos internacionais UN/LOCODE mais comuns
# Formato: código: (cidade, uf, país)
INTERNATIONAL_PORTS = {
    # Ásia - China
    "CNNGB": ("Ningbo", "", "China"),
    "CNSHA": ("Xangai", "", "China"),
    "CNQDG": ("Qingdao", "", "China"),
    "CNTAO": ("Tianjin", "", "China"),
    "CNCXD": ("Xingang", "", "China"),
    "CNSZX": ("Shenzhen", "", "China"),
    "CNNDG": ("Nansha", "", "China"),
    "CNXMN": ("Xiamen", "", "China"),
    "CNQIN": ("Qinhuangdao", "", "China"),
    "CNZZZ": ("China", "", "China"),
    # Ásia - Outros
    "SGSIN": ("Singapura", "", "Singapura"),
    "JPTYO": ("Tóquio", "", "Japão"),
    "JPOSA": ("Osaka", "", "Japão"),
    "JPNGS": ("Nagoya", "", "Japão"),
    "HKHKG": ("Hong Kong", "", "Hong Kong"),
    "KRPUS": ("Busan (Pusan)", "", "Coreia do Sul"),
    "KANIN": ("Incheon", "", "Coreia do Sul"),
    "KRPUS": ("Busan", "", "Coreia do Sul"),
    "VNCLI": ("Cat Lai", "", "Vietnã"),
    "VNXXX": ("Vietnã", "", "Vietnã"),
    "VNZZZ": ("Vietnã", "", "Vietnã"),
    "THBKK": ("Bangkok", "", "Tailândia"),
    "IDLHG": ("Jakarta", "", "Indonésia"),
    "IDJKT": ("Jacarta", "", "Indonésia"),
    "IDSUB": ("Surabaya", "", "Indonésia"),
    "MYPKG": ("Port Klang", "", "Malásia"),
    "MYSUB": ("Subang", "", "Malásia"),
    "PHPHI": ("Filipinas", "", "Filipinas"),
    "PHMNL": ("Manila", "", "Filipinas"),
    "BDCGP": ("Batangas", "", "Filipinas"),
    "INNSA": ("Nhava Sheva", "", "Índia"),
    "INMUN": ("Mundra", "", "Índia"),
    # Europa
    "NLRTM": ("Roterdã", "", "Países Baixos"),
    "NLXXX": ("Países Baixos", "", "Países Baixos"),
    "DEHAM": ("Hamburgo", "", "Alemanha"),
    "DEBRE": ("Bremerhaven", "", "Alemanha"),
    "DEBRV": ("Brêmea", "", "Alemanha"),
    "BEANR": ("Antuérpia", "", "Bélgica"),
    "BEBRU": ("Bruxelas", "", "Bélgica"),
    "FRLEH": ("Le Havre", "", "França"),
    "FRMRS": ("Marselha", "", "França"),
    "ESZZZ": ("Espanha", "", "Espanha"),
    "ESALG": ("Algeciras", "", "Espanha"),
    "ESBCN": ("Barcelona", "", "Espanha"),
    "ESVLC": ("Valência", "", "Espanha"),
    "ESTAR": ("Tarragona", "", "Espanha"),
    "ITGOA": ("Gênova", "", "Itália"),
    "ITTRI": ("Trieste", "", "Itália"),
    "ITLIO": ("Livorno", "", "Itália"),
    "GRPIR": ("Pireu", "", "Grécia"),
    "GBLGP": ("London Gateway", "", "Reino Unido"),
    "GBFXT": ("Felixstowe", "", "Reino Unido"),
    "GBSOU": ("Southampton", "", "Reino Unido"),
    "PTLIS": ("Lisboa", "", "Portugal"),
    "PTSIN": ("Sines", "", "Portugal"),
    # Oriente Médio
    "AEDXB": ("Dubai", "", "Emirados Árabes"),
    "AEAUH": ("Abu Dhabi", "", "Emirados Árabes"),
    "AEJEA": ("Jebel Ali", "", "Emirados Árabes"),
    "QAMCT": ("Doha", "", "Catar"),
    "OMSLL": ("Salalah", "", "Omã"),
    "OMSAL": ("Salalah", "", "Omã"),
    "IRBKM": ("Khorramshahr", "", "Irã"),
    "IRBND": ("Bandar Abbas", "", "Irã"),
    "IRAMM": ("Bandar Imam", "", "Irã"),
    "PKKHI": ("Karachi", "", "Paquistão"),
    "PKKET": ("Karachi", "", "Paquistão"),
    "SAJED": ("Jeddah", "", "Arábia Saudita"),
    "SADMM": ("Dammam", "", "Arábia Saudita"),
    # Américas - EUA
    "USNYC": ("Nova York", "NY", "Estados Unidos"),
    "USLAX": ("Los Angeles", "CA", "Estados Unidos"),
    "USHOU": ("Houston", "TX", "Estados Unidos"),
    "USSAV": ("Savannah", "GA", "Estados Unidos"),
    "USMIA": ("Miami", "FL", "Estados Unidos"),
    "USCHS": ("Charleston", "SC", "Estados Unidos"),
    "USSEA": ("Seattle", "WA", "Estados Unidos"),
    "USMSY": ("Nova Orleans", "LA", "Estados Unidos"),
    "USORF": ("Norfolk", "VA", "Estados Unidos"),
    "USMOB": ("Mobile", "AL", "Estados Unidos"),
    "USBAL": ("Baltimore", "MD", "Estados Unidos"),
    "USBOS": ("Boston", "MA", "Estados Unidos"),
    "USCHI": ("Chicago", "IL", "Estados Unidos"),
    "USDAL": ("Dallas", "TX", "Estados Unidos"),
    "USDET": ("Detroit", "MI", "Estados Unidos"),
    "USJAX": ("Jacksonville", "FL", "Estados Unidos"),
    "USLBE": ("Long Beach", "CA", "Estados Unidos"),
    "USNWK": ("Newark", "NJ", "Estados Unidos"),
    "USOAK": ("Oakland", "CA", "Estados Unidos"),
    "USPHL": ("Philadelphia", "PA", "Estados Unidos"),
    "USTPA": ("Tampa", "FL", "Estados Unidos"),
    "USZZZ": ("Estados Unidos", "", "Estados Unidos"),
    # Américas - Canadá
    "CAYVR": ("Vancouver", "BC", "Canadá"),
    "CAMTR": ("Montreal", "QC", "Canadá"),
    "CATOR": ("Toronto", "ON", "Canadá"),
    "CAHAL": ("Halifax", "NS", "Canadá"),
    # Américas - Brasil
    "BRSSZ": ("São Sebastião", "SP", "Brasil"),
    "BRRIO": ("Rio de Janeiro", "RJ", "Brasil"),
    "BRFOR": ("Fortaleza", "CE", "Brasil"),
    "BRADR": ("Brasil (Outros)", "", "Brasil"),
    # América do Sul
    "ARBUE": ("Buenos Aires", "", "Argentina"),
    "CLCLI": ("Callao", "", "Peru"),
    "CLVAP": ("Valparaíso", "", "Chile"),
    "PECLL": ("Callao", "", "Peru"),
    "ECGYE": ("Guayaquil", "", "Equador"),
    "COCTG": ("Cartagena", "", "Colômbia"),
    # África
    "ZADUR": ("Durban", "", "África do Sul"),
    "ZACPT": ("Cidade do Cabo", "", "África do Sul"),
    "EGALY": ("Alexandria", "", "Egito"),
    "EGZZZ": ("Egito", "", "Egito"),
    # Oceania
    "AUSYD": ("Sydney", "NSW", "Austrália"),
    "AUMEL": ("Melbourne", "VIC", "Austrália"),
    "NZAKL": ("Auckland", "", "Nova Zelândia"),
    # Códigos genéricos/ZZZ
    "XXXZZ": ("Outros", "", "Desconhecido"),
    "ZZZZZ": ("Desconhecido", "", "Desconhecido"),
}


class ReferentialHelper:
    """
    Helper for querying referential/lookup tables in BigQuery
    Provides methods to get friendly names for codes
    """

    def __init__(self, client=None):
        """
        Initialize the helper

        Args:
            client: BigQuery client (optional, will create if not provided)
        """
        if client is None:
            from google.cloud import bigquery
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
            self.client = bigquery.Client(project=project_id)
        else:
            self.client = client

        self.project = os.getenv("GOOGLE_CLOUD_PROJECT", "saasimpacto")
        self.dataset = "antaqdados.br_antaq_estatistico_aquaviario"
        self.international_ports = INTERNATIONAL_PORTS
        self._code_like_re = re.compile(r"^[0-9.\- /]+$")

    def _clean_value(self, value: Any) -> str:
        """Normalize values from BigQuery rows."""
        if value is None:
            return ""
        if isinstance(value, float) and pd.isna(value):
            return ""
        text = str(value).strip()
        if text.lower() in {"nan", "none"}:
            return ""
        return text

    def _is_code_like(self, text: str) -> bool:
        """Heuristic for codes (avoid showing them as names)."""
        if not text:
            return True
        if len(text) <= 2:
            return True
        return bool(self._code_like_re.match(text))

    def _pick_best_mercadoria_name(self, row: pd.Series, code: str) -> str:
        """
        Pick the best human-readable name for a commodity from a row.
        Prefers simplified names, then other descriptive fields, then group.
        """
        priority_cols = [
            "nomenclatura_simplificada",
            "mercadoria",
            "mercadoria_nome",
            "descricao_mercadoria",
            "descricao",
            "mercadoria_descricao",
            "ncm_descricao",
        ]

        for col in priority_cols:
            if col in row.index:
                value = self._clean_value(row[col])
                if value and value != code and not self._is_code_like(value):
                    return value

        # Try NCM if it's descriptive (not just a code)
        if "ncm" in row.index:
            value = self._clean_value(row["ncm"])
            if value and value != code and not self._is_code_like(value):
                return value

        # Fallback to any other descriptive columns, prefer shorter names
        candidates = []
        for col in row.index:
            if col in {"cd_mercadoria", "cdmercadoria", "string_field_0"}:
                continue
            if "container" in col or "tipo_container" in col:
                continue
            value = self._clean_value(row[col])
            if not value or value == code or self._is_code_like(value):
                continue
            candidates.append(value)

        if candidates:
            return min(candidates, key=len)

        # Last resort: group/legacy description
        for col in ("grupo_mercadoria", "string_field_3"):
            if col in row.index:
                value = self._clean_value(row[col])
                if value:
                    return value

        return code

    def get_mercadoria_nome(self, cd_mercadoria: str) -> str:
        """
        Get friendly name for commodity code.

        Prefers the simplified cargo name when available.

        Args:
            cd_mercadoria: Commodity code

        Returns:
            Friendly name or original code if not found
        """
        if not cd_mercadoria or str(cd_mercadoria) == 'nan':
            return str(cd_mercadoria) if cd_mercadoria else ""

        try:
            from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

            # Prefer schema-based columns
            query = f"""
            SELECT *
            FROM `{self.dataset}.mercadoria_carga`
            WHERE cd_mercadoria = @cd_mercadoria
            LIMIT 1
            """
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("cd_mercadoria", "STRING", str(cd_mercadoria))
                ]
            )

            result = self.client.query(query, job_config=job_config).to_dataframe()

            if not result.empty:
                row = result.iloc[0]
                code = self._clean_value(row.get("cd_mercadoria", cd_mercadoria))
                return self._pick_best_mercadoria_name(row, code or str(cd_mercadoria))
            return str(cd_mercadoria)

        except Exception:
            # Fallback for legacy tables with generic column names
            try:
                from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

                query = f"""
                SELECT *
                FROM `{self.dataset}.mercadoria_carga`
                WHERE string_field_0 = @cd_mercadoria
                LIMIT 1
                """
                job_config = QueryJobConfig(
                    query_parameters=[
                        ScalarQueryParameter("cd_mercadoria", "STRING", str(cd_mercadoria))
                    ]
                )

                result = self.client.query(query, job_config=job_config).to_dataframe()

                if not result.empty:
                    row = result.iloc[0]
                    code = self._clean_value(row.get("string_field_0", cd_mercadoria))
                    return self._pick_best_mercadoria_name(row, code or str(cd_mercadoria))
                return str(cd_mercadoria)

            except Exception as e:
                import logging
                logging.error(f"Error getting mercadoria name: {e}")
                return str(cd_mercadoria)

    def get_instalacao_destino_info(self, destino: str) -> Dict[str, str]:
        """
        Get destination information (city, UF, country)

        First checks international ports dictionary, then BigQuery table.

        Args:
            destino: Destination code (UN/LOCODE or Brazilian port code)

        Returns:
            Dictionary with cidade, uf, pais
        """
        from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

        info = {"cidade": "", "uf": "", "pais": ""}

        if not destino or str(destino) == 'nan' or str(destino) == 'Não informado':
            return info

        destino = str(destino).strip().upper()

        # 1. Check international ports dictionary first
        if destino in self.international_ports:
            cidade, uf, pais = self.international_ports[destino]
            return {"cidade": cidade, "uf": uf, "pais": pais}

        # 2. Check Brazilian/foreign ports table with multiple possible key columns
        try:
            def _query_destino(column_name: str) -> Optional[pd.Series]:
                query = f"""
                SELECT cidade, uf, pais
                FROM `{self.dataset}.instalacao_destino`
                WHERE {column_name} = @destino
                LIMIT 1
                """
                job_config = QueryJobConfig(
                    query_parameters=[
                        ScalarQueryParameter("destino", "STRING", destino)
                    ]
                )
                result = self.client.query(query, job_config=job_config).to_dataframe()
                if not result.empty:
                    return result.iloc[0]
                return None

            for col in ("origem", "destino", "codigo", "unlocode"):
                try:
                    row = _query_destino(col)
                except Exception:
                    row = None
                if row is not None:
                    info["cidade"] = row['cidade'] if pd.notna(row['cidade']) else ""
                    info["uf"] = row['uf'] if pd.notna(row['uf']) else ""
                    info["pais"] = row['pais'] if pd.notna(row['pais']) else ""
                    return info

            # 3. Fallback: try origem table too (some codes live there)
            origem_info = self.get_instalacao_origem_info(destino)
            if any(origem_info.values()):
                return origem_info

            # 4. Fallback: derive country from UN/LOCODE prefix
            if len(destino) == 5 and destino[:2].isalpha():
                country = self._get_country_from_unlocode(destino[:2])
                if country:
                    info["pais"] = country
            return info

        except Exception as e:
            import logging
            logging.error(f"Error getting destino info: {e}")
            return info

    def _get_country_from_unlocode(self, country_code: str) -> str:
        """Return country name (pt-BR) from UN/LOCODE prefix."""
        if not country_code:
            return ""
        code = country_code.upper()
        # Minimal mapping for common destinations
        map_pt = {
            "CN": "China",
            "US": "Estados Unidos",
            "AR": "Argentina",
            "CL": "Chile",
            "PE": "Peru",
            "CO": "Colômbia",
            "EC": "Equador",
            "MX": "México",
            "DE": "Alemanha",
            "ES": "Espanha",
            "FR": "França",
            "IT": "Itália",
            "NL": "Países Baixos",
            "BE": "Bélgica",
            "GB": "Reino Unido",
            "PT": "Portugal",
            "EG": "Egito",
            "ZA": "África do Sul",
            "TR": "Turquia",
            "IN": "Índia",
            "JP": "Japão",
            "KR": "Coreia do Sul",
            "AE": "Emirados Árabes",
            "SA": "Arábia Saudita",
            "QA": "Catar",
            "SG": "Singapura",
            "AU": "Austrália",
            "CA": "Canadá",
            "BR": "Brasil",
        }
        if code in map_pt:
            return map_pt[code]
        # Try pycountry if available
        try:
            import pycountry
            country = pycountry.countries.get(alpha_2=code)
            if country:
                return country.name
        except Exception:
            pass
        return ""

    def get_instalacao_origem_info(self, origem: str) -> Dict[str, str]:
        """
        Get origin information (city, UF, country)

        First checks international ports dictionary, then BigQuery table.

        Args:
            origem: Origin code (UN/LOCODE or Brazilian port code)

        Returns:
            Dictionary with cidade, uf, pais
        """
        from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter

        info = {"cidade": "", "uf": "", "pais": ""}

        if not origem or str(origem) == 'nan':
            return info

        origem = str(origem).strip().upper()

        # 1. Check international ports dictionary first
        if origem in self.international_ports:
            cidade, uf, pais = self.international_ports[origem]
            return {"cidade": cidade, "uf": uf, "pais": pais}

        # 2. Check Brazilian ports table
        try:
            query = f"""
            SELECT cidade, uf, pais
            FROM `{self.dataset}.instalacao_origem`
            WHERE origem = @origem
            LIMIT 1
            """
            job_config = QueryJobConfig(
                query_parameters=[
                    ScalarQueryParameter("origem", "STRING", origem)
                ]
            )

            result = self.client.query(query, job_config=job_config).to_dataframe()

            if not result.empty:
                row = result.iloc[0]
                info["cidade"] = row['cidade'] if pd.notna(row['cidade']) else ""
                info["uf"] = row['uf'] if pd.notna(row['uf']) else ""
                info["pais"] = row['pais'] if pd.notna(row['pais']) else ""

            return info

        except Exception as e:
            import logging
            logging.error(f"Error getting origem info: {e}")
            return info

    def enrich_destino_with_info(self, destino: str) -> str:
        """
        Get a friendly description for a destination (City, UF - Country)

        Args:
            destino: Destination code

        Returns:
            Friendly string like "Santos, SP - Brasil" or original code
        """
        info = self.get_instalacao_destino_info(destino)

        parts = []
        if info["cidade"]:
            parts.append(info["cidade"])
        if info["uf"]:
            parts.append(info["uf"])

        # Build the friendly string
        if parts and info["pais"]:
            return f"{', '.join(parts)} - {info['pais']}"
        elif parts:
            return ', '.join(parts)
        elif info["pais"]:
            return info["pais"]
        else:
            return destino

    def batch_get_mercadoria_nomes(self, codigos: list) -> Dict[str, str]:
        """
        Batch lookup for multiple commodity codes

        Args:
            codigos: List of commodity codes

        Returns:
            Dictionary mapping code -> friendly name
        """
        if not codigos:
            return {}

        # Remove None and 'nan' values
        valid_codes = [c for c in codigos if c and str(c) != 'nan']

        if not valid_codes:
            return {}

        try:
            # Create IN clause with up to 1000 codes (BigQuery limit)
            codes_str = ", ".join([f"'{c}'" for c in valid_codes[:1000]])

            # Prefer schema-based columns
            query = f"""
            SELECT *
            FROM `{self.dataset}.mercadoria_carga`
            WHERE cd_mercadoria IN ({codes_str})
            """

            result = self.client.query(query).to_dataframe()

            mapping = {}
            code_col = "cd_mercadoria" if "cd_mercadoria" in result.columns else None
            for _, row in result.iterrows():
                code = self._clean_value(row.get(code_col)) if code_col else ""
                if not code:
                    continue
                mapping[code] = self._pick_best_mercadoria_name(row, code)

            # Add codes not found in result
            for code in valid_codes:
                code_str = str(code)
                if code_str not in mapping:
                    mapping[code_str] = code_str

            return mapping

        except Exception:
            # Fallback for legacy tables with generic column names
            try:
                codes_str = ", ".join([f"'{c}'" for c in valid_codes[:1000]])

                query = f"""
                SELECT *
                FROM `{self.dataset}.mercadoria_carga`
                WHERE string_field_0 IN ({codes_str})
                """

                result = self.client.query(query).to_dataframe()

                mapping = {}
                code_col = "string_field_0" if "string_field_0" in result.columns else None
                for _, row in result.iterrows():
                    code = self._clean_value(row.get(code_col)) if code_col else ""
                    if not code:
                        continue
                    mapping[code] = self._pick_best_mercadoria_name(row, code)

                for code in valid_codes:
                    code_str = str(code)
                    if code_str not in mapping:
                        mapping[code_str] = code_str

                return mapping

            except Exception as e:
                import logging
                logging.error(f"Error in batch mercadoria lookup: {e}")
                return {str(c): str(c) for c in valid_codes}


# Cached instance for reuse
_cached_helper: Optional[ReferentialHelper] = None


def get_referential_helper(client=None) -> ReferentialHelper:
    """
    Get a cached ReferentialHelper instance

    Args:
        client: BigQuery client (optional)

    Returns:
        ReferentialHelper instance
    """
    global _cached_helper

    if _cached_helper is None:
        _cached_helper = ReferentialHelper(client)

    return _cached_helper
