from algos.base_algo import AlgoBase
from typing import List, Dict

class NewAlgorithm(AlgoBase):
    """Description de votre algorithme"""
    
    @property
    def name(self) -> str:
        return "Test_Algorithme"
        
    def analyze_race(self, race: Dict) -> List[int]:
        """Analyse une course et retourne 5 chevaux"""
        try:
            # Filtrer les partants valides
            partants = self.filter_valid_runners(race['partants'])
            if not partants:
                return []
            
            # Variables utiles
            valid_runners = []
            for partant in partants:
                # Récupérer la cote
                odds = self.get_odds(partant, race)
                if odds <= 0:
                    continue
                    
                # Récupérer les coefficients
                forme_score = (
                    float(partant.get('coeff_forme_cheval', 0)) * 1.5 +
                    float(partant.get('coeff_forme_jockey', 0)) * 0.8 +
                    float(partant.get('coeff_forme_entraineur', 0)) * 0.7
                )
                
                appetence_score = (
                    float(partant.get('appetence_corde', 0)) +
                    float(partant.get('appetence_sol', 0)) * 1.2 +
                    float(partant.get('appetence_distance', 0)) * 1.3
                )
                
                # Score final
                final_score = (forme_score * 0.6 + appetence_score * 0.4) / odds
                
                valid_runners.append((int(partant['numero']), final_score))
            
            # Trier par score et retourner les 5 meilleurs
            sorted_runners = sorted(valid_runners, key=lambda x: x[1], reverse=True)
            return [r[0] for r in sorted_runners[:5]]
            
        except Exception as e:
            print(f"Erreur dans {self.name}: {e}")
            return []
