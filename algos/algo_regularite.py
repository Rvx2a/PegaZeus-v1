from algos.base_algo import AlgoBase
from typing import List, Dict
import re

class AlgoRegularite(AlgoBase):
    """Algorithme basé sur la régularité et la forme récente"""
    
    @property
    def name(self) -> str:
        return "Algo_Regularite_v1"
        
    def _analyze_musique(self, musique: str) -> tuple:
        """Analyse la musique d'un cheval"""
        if not musique:
            return (0, 0)
            
        # Nettoie la musique
        musique = re.sub(r'[^\d]', '', musique[:10])  # Garde les 10 premiers chiffres
        if not musique:
            return (0, 0)
            
        # Calcule le score de régularité et la forme
        positions = [int(x) for x in musique]
        regularite = sum(1 for x in positions if x <= 3) / len(positions)
        forme = sum(1 / x if x > 0 else 0 for x in positions[:3]) / 3
        
        return (regularite, forme)
        
    def analyze_race(self, race: Dict) -> List[int]:
        """Analyse une course et retourne 5 chevaux"""
        try:
            # Filtrer les partants valides
            partants = self.filter_valid_runners(race['partants'])
            if not partants:
                return []
                
            # Évalue chaque partant
            valid_runners = []
            for partant in partants:
                # Récupère la cote
                odds = self.get_odds(partant, race)
                if odds <= 0:
                    continue
                    
                # Analyse la musique
                regularite, forme = self._analyze_musique(partant.get('musique', ''))
                
                # Score de forme global
                forme_score = (
                    float(partant.get('coeff_forme_cheval', 0)) * 2.0 +
                    float(partant.get('coeff_forme_jockey', 0)) * 1.0 +
                    float(partant.get('coeff_forme_entraineur', 0)) * 0.5 +
                    forme * 2.0
                ) / 5.5
                
                # Score d'appétence
                appetence_score = (
                    float(partant.get('appetence_corde', 0)) * 0.8 +
                    float(partant.get('appetence_sol', 0)) * 1.2 +
                    float(partant.get('appetence_distance', 0)) * 1.5
                ) / 3.5
                
                # Score de régularité
                regularite_score = regularite * 10
                
                # Score final
                final_score = (
                    forme_score * 0.4 +
                    appetence_score * 0.3 +
                    regularite_score * 0.3
                ) / (odds ** 0.5)  # Utilise la racine carrée de la cote pour réduire son impact
                
                valid_runners.append((int(partant['numero']), final_score))
            
            # Trie par score et retourne les 5 meilleurs
            sorted_runners = sorted(valid_runners, key=lambda x: x[1], reverse=True)
            return [r[0] for r in sorted_runners[:5]]
            
        except Exception as e:
            print(f"Erreur dans {self.name}: {e}")
            return []
