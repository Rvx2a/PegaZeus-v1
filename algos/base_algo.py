from abc import ABC, abstractmethod
from typing import List, Dict

class AlgoBase(ABC):
    """Classe abstraite pour les algorithmes de prédiction"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Nom de l'algorithme"""
        pass
        
    @abstractmethod
    def analyze_race(self, race: Dict) -> List[int]:
        """Analyse une course et retourne une liste de numéros de chevaux
        
        Args:
            race (Dict): Données de la course à analyser
            
        Returns:
            List[int]: Liste des numéros de chevaux prédits (max 5)
        """
        pass
        
    def filter_valid_runners(self, runners: List[Dict]) -> List[Dict]:
        """Filtre les partants valides (non NP)"""
        return [r for r in runners if r.get('numero') != 'NP']
        
    def get_odds(self, runner: Dict, race: Dict) -> float:
        """Récupère la cote d'un partant selon le type configuré
        
        Args:
            runner (Dict): Données du partant
            race (Dict): Données de la course
            
        Returns:
            float: Cote du partant (0.0 si non disponible)
        """
        try:
            odds_type = race.get('odds_type', 'pmu')
            odds_str = runner.get(odds_type, 'NC')
            if odds_str == 'NC':
                return 0.0
            return float(str(odds_str).replace(',', '.'))
        except (ValueError, TypeError):
            return 0.0
