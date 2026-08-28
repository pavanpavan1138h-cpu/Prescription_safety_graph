import os
import json
import time
import logging
import hashlib
import requests
import pandas as pd
from pathlib import Path
from urllib.parse import quote

logger = logging.getLogger(__name__)

class RxNormCache:
    """
    Handles file-based caching for API responses to prevent redundant queries.
    """
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.categories = [
            "drugbank_identifier_lookup",
            "pubchem_cid_lookup",
            "pubchem_inchikey_lookup",
            "name_lookup",
            "approximate_lookup",
            "rxcui_properties"
        ]
        for cat in self.categories:
            (self.cache_dir / cat).mkdir(parents=True, exist_ok=True)

    def _get_path(self, category: str, key: str) -> Path:
        # Use MD5 hash of key to avoid file name issues with special characters
        safe_key = hashlib.md5(str(key).strip().lower().encode('utf-8')).hexdigest()
        return self.cache_dir / category / f"{safe_key}.json"

    def get(self, category: str, key: str) -> dict | None:
        path = self._get_path(category, key)
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error reading cache for {category}/{key}: {e}")
        return None

    def set(self, category: str, key: str, data: dict):
        path = self._get_path(category, key)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.warning(f"Error writing cache for {category}/{key}: {e}")

class RxNavClient:
    """
    HTTP client for querying NLM RxNav REST APIs and PubChem fallback APIs.
    Includes rate limiting, retries, exponential backoff, and caching.
    """
    def __init__(self, cache: RxNormCache, timeout: int = 10, max_retries: int = 3, delay_secs: float = 0.2):
        self.cache = cache
        self.timeout = timeout
        self.max_retries = max_retries
        self.delay_secs = delay_secs
        self.rxnav_base = "https://rxnav.nlm.nih.gov/REST"
        self.pubchem_base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"

    def _request(self, url: str, is_rxnav: bool = True) -> dict | None:
        for attempt in range(self.max_retries):
            try:
                # Basic rate limiting delay
                time.sleep(self.delay_secs * (2 ** attempt))
                response = requests.get(url, timeout=self.timeout)
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    return {"status": "not_found", "error_code": 404}
                else:
                    logger.warning(f"API returned status {response.status_code} for URL: {url}")
            except Exception as e:
                logger.warning(f"Attempt {attempt+1} failed for URL {url}: {e}")
        return None

    def lookup_by_drugbank_id(self, db_id: str) -> dict | None:
        cached = self.cache.get("drugbank_identifier_lookup", db_id)
        if cached:
            return cached
        url = f"{self.rxnav_base}/rxcui.json?idtype=DRUGBANK&id={db_id}"
        res = self._request(url)
        if res:
            self.cache.set("drugbank_identifier_lookup", db_id, res)
        return res

    def lookup_pubchem_cid_title(self, cid: str) -> dict | None:
        # Extract numeric CID if string format is used (e.g. CID000002173 -> 2173)
        clean_cid = ''.join(filter(str.isdigit, str(cid)))
        cached = self.cache.get("pubchem_cid_lookup", clean_cid)
        if cached:
            return cached
        url = f"{self.pubchem_base}/compound/cid/{clean_cid}/property/Title/JSON"
        res = self._request(url, is_rxnav=False)
        if res:
            self.cache.set("pubchem_cid_lookup", clean_cid, res)
        return res

    def lookup_pubchem_inchikey_title(self, inchikey: str) -> dict | None:
        cached = self.cache.get("pubchem_inchikey_lookup", inchikey)
        if cached:
            return cached
        url = f"{self.pubchem_base}/compound/inchikey/{inchikey}/property/Title/JSON"
        res = self._request(url, is_rxnav=False)
        if res:
            self.cache.set("pubchem_inchikey_lookup", inchikey, res)
        return res

    def lookup_by_name(self, name: str) -> dict | None:
        cached = self.cache.get("name_lookup", name)
        if cached:
            return cached
        url = f"{self.rxnav_base}/rxcui.json?name={quote(name)}"
        res = self._request(url)
        if res:
            self.cache.set("name_lookup", name, res)
        return res

    def lookup_approximate(self, term: str) -> dict | None:
        cached = self.cache.get("approximate_lookup", term)
        if cached:
            return cached
        url = f"{self.rxnav_base}/approximateTerm.json?term={quote(term)}&maxEntries=5"
        res = self._request(url)
        if res:
            self.cache.set("approximate_lookup", term, res)
        return res

    def get_rxcui_properties(self, rxcui: str) -> dict | None:
        cached = self.cache.get("rxcui_properties", rxcui)
        if cached:
            return cached
        url = f"{self.rxnav_base}/rxcui/{rxcui}/properties.json"
        res = self._request(url)
        if res:
            self.cache.set("rxcui_properties", rxcui, res)
        return res

class DrugNameResolver:
    """
    Resolves name candidates from multiple sources following a priority hierarchy.
    """
    def __init__(self, client: RxNavClient):
        self.client = client

    def resolve_name(self, drug_row: dict, source_mappings: pd.DataFrame) -> dict:
        """
        Returns: {
            "name_candidate": str or None,
            "name_source": str,
            "name_resolution_status": str,
            "provenance_notes": str
        }
        """
        internal_id = drug_row["internal_drug_id"]
        mappings = source_mappings[source_mappings["internal_drug_id"] == internal_id]
        
        db_mappings = mappings[mappings["source_dataset"] == "drugbank"]
        ts_mappings = mappings[mappings["source_dataset"] == "twosides"]
        
        # Priority 1: Check if we can get a title by querying DrugBank ID on RxNav
        # Wait, if we fetch properties from RxNorm by DrugBank ID directly, we get the clinical name!
        if not db_mappings.empty:
            db_id = db_mappings.iloc[0]["source_drug_id"]
            res = self.client.lookup_by_drugbank_id(db_id)
            if res and "idGroup" in res and "rxnormId" in res["idGroup"]:
                rxcuis = res["idGroup"]["rxnormId"]
                if len(rxcuis) == 1:
                    props = self.client.get_rxcui_properties(rxcuis[0])
                    if props and "properties" in props and "name" in props["properties"]:
                        return {
                            "name_candidate": props["properties"]["name"],
                            "name_source": "rxnav_drugbank_id_lookup",
                            "name_resolution_status": "AUTHORITATIVE_NAME",
                            "provenance_notes": f"Resolved clinical name via DrugBank ID {db_id} from RxNav properties."
                        }

        # Priority 2: Use PubChem Title API for TWOSIDES (PubChem CID)
        if not ts_mappings.empty:
            ts_id = ts_mappings.iloc[0]["source_drug_id"]
            res = self.client.lookup_pubchem_cid_title(ts_id)
            if res and "PropertyTable" in res and "Properties" in res["PropertyTable"]:
                props = res["PropertyTable"]["Properties"]
                if props and len(props) > 0 and "Title" in props[0]:
                    return {
                        "name_candidate": props[0]["Title"],
                        "name_source": "pubchem_cid_lookup",
                        "name_resolution_status": "PUBCHEM_TITLE_CANDIDATE",
                        "provenance_notes": f"Resolved title via PubChem CID {ts_id} title query."
                    }

        # Priority 3: Resolve via InChIKey lookup to PubChem if available
        inchikey = drug_row.get("inchikey")
        if pd.notna(inchikey) and isinstance(inchikey, str) and inchikey.strip():
            res = self.client.lookup_pubchem_inchikey_title(inchikey.strip())
            if res and "PropertyTable" in res and "Properties" in res["PropertyTable"]:
                props = res["PropertyTable"]["Properties"]
                if props and len(props) > 0 and "Title" in props[0]:
                    return {
                        "name_candidate": props[0]["Title"],
                        "name_source": "pubchem_inchikey_lookup",
                        "name_resolution_status": "PUBCHEM_TITLE_CANDIDATE",
                        "provenance_notes": f"Resolved title via PubChem InChIKey {inchikey} query."
                    }

        return {
            "name_candidate": None,
            "name_source": "none",
            "name_resolution_status": "NO_NAME_CANDIDATE",
            "provenance_notes": "Could not resolve a name candidate via DrugBank ID, PubChem CID, or InChIKey."
        }

class RxNormMatcher:
    """
    Applies matching rules to name candidates to resolve exact, normalized, or approximate RxCUIs.
    """
    def __init__(self, client: RxNavClient):
        self.client = client

    def match(self, name: str) -> dict:
        """
        Matches name candidates against RxNorm APIs.
        Returns match dict with keys: rxcui, rxnorm_name, rxnorm_match_status, rxnorm_match_method, candidates (list)
        """
        result = {
            "rxcui": None,
            "rxnorm_name": None,
            "rxnorm_synonym": None,
            "rxnorm_tty": None,
            "rxnorm_language": None,
            "rxnorm_match_status": "NO_MATCH",
            "rxnorm_match_method": "none",
            "match_score": 0.0,
            "candidates": []
        }
        if not name:
            return result

        # 1. Exact Name Lookup
        res = self.client.lookup_by_name(name)
        if res and "idGroup" in res and "rxnormId" in res["idGroup"]:
            rxcuis = res["idGroup"]["rxnormId"]
            # Extract details
            for rxcui in rxcuis:
                props = self.client.get_rxcui_properties(rxcui)
                if props and "properties" in props:
                    p = props["properties"]
                    candidate = {
                        "rxcui": rxcui,
                        "name": p.get("name"),
                        "synonym": p.get("synonym"),
                        "tty": p.get("tty"),
                        "language": p.get("language"),
                        "match_method": "exact_name_lookup",
                        "match_score": 100.0
                    }
                    result["candidates"].append(candidate)
            
            if len(rxcuis) == 1:
                final = result["candidates"][0]
                result.update({
                    "rxcui": final["rxcui"],
                    "rxnorm_name": final["name"],
                    "rxnorm_synonym": final["synonym"],
                    "rxnorm_tty": final["tty"],
                    "rxnorm_language": final["language"],
                    "rxnorm_match_status": "HIGH_EXACT",
                    "rxnorm_match_method": "exact_name_lookup",
                    "match_score": 100.0
                })
                return result
            elif len(rxcuis) > 1:
                result["rxnorm_match_status"] = "AMBIGUOUS_MATCH"
                result["rxnorm_match_method"] = "exact_name_lookup"
                return result

        # 2. Approximate Fallback Lookup
        approx_res = self.client.lookup_approximate(name)
        if approx_res and "approximateGroup" in approx_res and "candidate" in approx_res["approximateGroup"]:
            candidates = approx_res["approximateGroup"]["candidate"]
            for cand in candidates:
                rxcui = cand.get("rxcui")
                score = float(cand.get("score", 0))
                # Only keep candidate if score is high enough (e.g. > 50) and RxCUI matches
                if score >= 50 and rxcui:
                    props = self.client.get_rxcui_properties(rxcui)
                    if props and "properties" in props:
                        p = props["properties"]
                        result["candidates"].append({
                            "rxcui": rxcui,
                            "name": p.get("name"),
                            "synonym": p.get("synonym"),
                            "tty": p.get("tty"),
                            "language": p.get("language"),
                            "match_method": "approximate_lookup",
                            "match_score": score
                        })
            
            # Filter and choose high score candidate
            valid_candidates = [c for c in result["candidates"] if c["match_score"] >= 70]
            if len(valid_candidates) == 1:
                final = valid_candidates[0]
                result.update({
                    "rxcui": final["rxcui"],
                    "rxnorm_name": final["name"],
                    "rxnorm_synonym": final["synonym"],
                    "rxnorm_tty": final["tty"],
                    "rxnorm_language": final["language"],
                    "rxnorm_match_status": "LOW_APPROXIMATE",
                    "rxnorm_match_method": "approximate_lookup",
                    "match_score": final["match_score"]
                })
                return result
            elif len(valid_candidates) > 1:
                result["rxnorm_match_status"] = "AMBIGUOUS_MATCH"
                result["rxnorm_match_method"] = "approximate_lookup"
                return result

        return result
