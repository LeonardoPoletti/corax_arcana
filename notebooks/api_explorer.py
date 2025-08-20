#!/usr/bin/env python3
#/notebook/api_explorer.py
"""
Explorador API Scryfall - KyberCorax
Script para explorar e entender a estrutura da API Scryfall

Autor: Leonardo - Engenheiro de Dados
"""

import requests
import json
import time
from pathlib import Path
from loguru import logger
from typing import Dict, Any, List, Optional

# Configuração de logging
logger.add("logs/api_exploration.log",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {function} | {message}", 
           level="INFO")

class ScryfallExplorer:
    """
    Classe para explorar a API Scryfall de forma estruturada

    Princípios de Engenharia de Dados aplicadas:
    - Rate limiting respeitoso
    - Logging detalhado
    - Error handling robusto
    - Estrutura de dados clara
    """

    def __init__(self):
        self.base_url = "https://api.scryfall.com"
        self.session = requests.Session()

        # Headers recomendados para boa prática
        self.session.headers.update({
            'User-Agent': 'KyberCorax-DataPipeline/1.0 (Educational Purpose)', 
            'Accept': 'application/json'
        })

        # Rate limiting - Scryfall recomenda máximo 10 requests por segundo
        self.request_delay = 0.1 # 100ms entre requests

        logger.info("ScryfallExplorer inicializado")

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Método privado para fazer requisições com tratamento de erro

        Args:
            endpoint: Endpoint da API
            params: Parâmetros da query string

        Returns: 
            Dicionário com resposta JSN ou None em caso de erro
        """
        url = f"{self.base_url}{endpoint}"

        try:
            logger.info(f"Fazendo requisição para: {url}")
            if params:
                logger.info(f"Parâmetros: {params}")

            # Rate limiting respeitoso
            time.sleep(self.request_delay)

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status() # Raise exception para status HTTPS de erro

            logger.success(f"Requisição bem-sucessida - Status: {response.status_code}")
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para {url}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar JSON de {url}: {e}")
            return None
        
    def explore_sets(self, limit: int = 5) -> Dict[str, Any]:
        """
        Explora o endpoint /sets para entender estrutura dos sets

        Args:
            limit: Número de sets para analisar em detalhes

        Returns:
            Dicionário com análise dos sets
        """
        logger.info("Explorando endpoint /sets")

        sets_data = self._make_request("/sets")
        if not sets_data:
            return {"error": "Falha ao obter dados dos sets"}
        
        # Analisar primeiros sets em detalhes
        analysis = {
            "total_sets": len(sets_data.get('data', [])),
            #"total_sets_analysed": len(set_data.get())
            "structure_keys": list(sets_data.keys()),
            "sample_sets": [],
            "set_types": set(),
            "date_range": {"oldest": None, "newest": None}
        }

        # Analisar primeiros sets em detalhes
        for i, set_data in enumerate(sets_data.get('data', [])[:limit]):
            set_info = {
                "object": set_data.get('object'),
                "code": set_data.get('code'),
                "name": set_data.get('name'),
                "set_type": set_data.get('set_type'),
                "card_count":set_data.get('card_count'),
                "released_at": set_data.get('released_at'),
                "keys": list(set_data.keys())
            }

            analysis["sample_sets"].append(set_info)
            analysis["set_types"].add(set_data.get('set_type'))

            # Análise temporal
            release_date = set_data.get('released_at')
            if release_date:
                if not analysis["date_range"]["oldest"] or release_date < analysis["date_range"]["oldest"]:
                    analysis["date_range"]["oldest"] = release_date
                if not analysis["date_range"]["newest"] or release_date > analysis["date_range"]["newest"]:
                    analysis["date_range"]["newest"] = release_date
        analysis["set_types"] = list(analysis["set_types"])

        logger.info(f"Análise dos sets: {len(analysis["sample_sets"])} sets análisados")
        logger.info(f"Análise completa: {analysis['total_sets']} sets encontrados")
        
        return analysis
    
    def explore_cards(self, set_core: str = "inr", limit: int = 5) -> Dict[str, Any]:
        """
        Explora o endpoint /cards/search para entender estrutura das cartas

        Args:
            set_code: Código do set para buscar cartas
            limit: Número de cartas para analisar

        Returns:
            Dicionário com análise das cartas
        """
        logger.info(f"Explorando cartas do set: {set_core}")

        params = {"q": f"set:{set_core}", "page": 1}
        cards_data = self._make_request("/cards/search", params)

        if not cards_data:
            return {"error": f"Falha ao obter cartas do set {set_core}"}
        
        # Análise estrutural
        analysis = {
            "total_cards": cards_data.get('total_cards', 0),
            "has_more": cards_data.get('has_more', False),
            "structure_keys": list(cards_data.keys()),
            "sample_cards": [],
            "card_types": set(),
            "colors": set(),
            "rarities": set(),
            "languages": set()
        }

        # Analisar cartas em detalhes
        for i, card in enumerate(cards_data.get('data', [])[:limit]):
            card_info = {
                "name": card.get("name"),
                "mana_cost": card.get("mana_cost"),
                "type_line": card.get("type_line"),
                "rarity": card.get("rarity"),
                "colors": card.get("colors", []),
                "set": card.get("set"),
                "lang": card.get("lang"),
                "keys": list(card.keys()),
                "total_keys": len(card.keys())
            }

            analysis["sample_cards"].append(card_info)

            # Agregações para análise
            if card.get('type_line'):
                analysis["card_types"].add(card.get('type_line').split('-')[0].strip())
            if card.get('rarity'):
                analysis["rarities"].add(card.get('rarity'))
            if card.get('colors'):
                analysis["colors"].update(card.get('colors'))
            if card.get('lang'):
                analysis["languages"].add(card.get('lang'))

        # Converter sets para listas
        analysis["card_types"] = list(analysis["card_types"])
        analysis["colors"] = list(analysis["colors"])
        analysis["rarities"] = list(analysis["rarities"])
        analysis["languages"] = list(analysis["languages"])

        logger.info(f"Análise completa: {analysis['total_cards']} cartas no set {set_core}")
        return analysis
    
#    def explore_catalog(self, catalog_type: str = "card-names") -> Dict[str, Any]:
#        """
#        Explora o endpoint /catalog para metados
#
#        Args:
#            catalog_type: Tipo de catálogo (card-names, creature-types, etc.)
#
#        Returns:
#            Dicionário com análise do catálogo
#        """
#        logger.info(f"Explorando catálogo: {catalog_type}")
#
#        catalog_data = self._make_request(f"/catalog/{catalog_type}")
#
#        if not catalog_data:
#            return {"error": f"Falha ao obter catálogo {catalog_type}"}
#        
#        analysis = {
#            "catalog_type": catalog_type,
#            "total_items": len(catalog_data.get('data', [])),
#            "structure_keys": list(catalog_data.keys()),
#            "sample_items": catalog_data.get('data', [])[:10],
#            "uri": catalog_data.get('uri')
#        }
#
#        logger.info(f"Catálogo {catalog_type}: {analysis['total_items']} itens")
#        return analysis
#    
    def save_exploration_results(self, results: Dict[str, Any], filename: str):
        """
        Salva resultados da exploração em arquivo JSON

        Args:
            results: Dados para salvar
            filename: Nome do arquivo
        """
        # Criar diretório se não exister
        Path("data/exploration").mkdir(parents=True, exist_ok=True)

        filepath = f"data/exploration/{filename}"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.success(f"Resultados salvos em: {filepath}")
        except Exception as e:
            logger.error(f"Erro ao salvar {filepath}: {e}")

def main():
    """Função principal para exploração da API"""
    logger.info("Iniciando exploração da API Scryfall")

    # Criar diretório de logs
    Path("logs").mkdir(exist_ok=True)

    explorer = ScryfallExplorer()

    # Exploraçóo estruturada
    print("Explorando Sets...")
    sets_analysis = explorer.explore_sets(limit=20)
    explorer.save_exploration_results(sets_analysis, "sets_analysis.json")

    print("Explorando Cartas...")
    cards_analysis = explorer.explore_cards(set_core="inr", limit=5)
    print(cards_analysis)
#    explorer.save_exploration_results(cards_analysis, "cards_analysis.json")
#
#    print("Explorando Catálogos...")
#    catalog_types = ["creature-types", "card-names", "supertypes"]
#
#    for catalog in catalog_types:
#        catalog_analysis = explorer.explore_catalog(catalog)
#        explorer.save_exploration_results(
#            catalog_analysis,
#            f"catalog_{catalog.replace('-', '_')}_analysis.json"
#        )
#        time.sleep(0.2) # Rate limiting extra para múltiplas requisições
#
#    # Resumo final
#    print("\n" + "="*60)
#    print("RESUMO DA EXPLORAÇÃO")
#    print("="*60)
#    print(f"Total de Sets: {sets_analysis.get('total_sets', 'N/A')}")
#    print(f"Cartas analisadas: {cards_analysis.get('total_cards', 'N/A')}")
#    print(f"Catálogos explorados: {len(catalog_types)}")
#    print(f"Arquivos gerados: data/exploration/")
#    print(f"Logs: logs/api_exploration.log")
#    print("="*60)
#    
#    logger.info("Exploração da API Scryfall concluída")
#
if __name__ == "__main__":
    main()