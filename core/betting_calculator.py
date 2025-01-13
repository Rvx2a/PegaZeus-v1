from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class BettingResult:
    """Résultat d'un pari"""
    type_pari: str
    operateur: str
    mise_unitaire: float
    mise_totale: float
    gains_bruts: float
    gains_nets: float
    roi: float
    details: List[str]
    options: Dict  # Options spécifiques au type de pari (ex: ordre/désordre pour Tiercé)

class BettingCalculator:
    """Calculateur de gains pour les différents types de paris"""
    
    def __init__(self, operateur: str = "PMU"):
        self.operateur = operateur
        self.mise_base = {
            "Simple": 1.0,
            "Couplé": 1.0,
            "2 sur 4": 3.0,
            "Trio": 1.0,
            "Tiercé": 1.0,
            "Quarté": 1.30,
            "Quinté": 2.0,
            "Multi": 3.0
        }
        
    def get_available_bets(self, course: Dict) -> List[str]:
        """Retourne les paris disponibles pour une course"""
        paris_dispo = []
        for pari in course.get('paris_disponibles', []):
            if pari.get('disponible', False):
                nom = pari['nom'].replace('Jeu ', '')
                paris_dispo.append(nom)
        return paris_dispo

    def calculate_course_gains(self, course: Dict, predictions: List[int], selected_bets: List[str] = None) -> Dict[str, BettingResult]:
        """Calcule les gains pour tous les types de paris sélectionnés d'une course
        
        Args:
            course: Données de la course
            predictions: Liste des numéros prédits
            selected_bets: Liste des types de paris à calculer (None = tous les paris disponibles)
        
        Returns:
            Dict des résultats par type de pari
        """
        results = {}
        paris_disponibles = self.get_available_bets(course)
        
        if selected_bets is None:
            selected_bets = paris_disponibles
        
        for type_pari in selected_bets:
            if type_pari in paris_disponibles:
                results[type_pari] = self.calculate_bet_gains(course, predictions, type_pari)
                
        return results

    def calculate_bet_gains(self, course: Dict, predictions: List[int], type_pari: str) -> BettingResult:
        """Calcule les gains pour un type de pari spécifique"""
        predictions = [str(p) for p in predictions]
        arrivee = [str(x) for x in course['infos_course'].get('arrivee', [])]
        
        result = BettingResult(
            type_pari=type_pari,
            operateur=self.operateur,
            mise_unitaire=self.mise_base[type_pari],
            mise_totale=0,
            gains_bruts=0,
            gains_nets=0,
            roi=0,
            details=[],
            options={}
        )

        rapports = course.get('rapports', {}).get(type_pari, [])
        rapports_operateur = [r for r in rapports if r['operateur'] == self.operateur]

        if type_pari == "Simple":
            result = self._calculate_simple(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Couplé":
            result = self._calculate_couple(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "2 sur 4":
            result = self._calculate_deux_sur_quatre(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Trio":
            result = self._calculate_trio(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Tiercé":
            result = self._calculate_tierce(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Quarté":
            result = self._calculate_quarte(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Quinté":
            result = self._calculate_quinte(predictions, arrivee, rapports_operateur, result)
        elif type_pari == "Multi":
            result = self._calculate_multi(predictions, arrivee, rapports_operateur, result)

        # Calcul du ROI
        if result.mise_totale > 0:
            result.gains_nets = result.gains_bruts - result.mise_totale
            result.roi = (result.gains_nets / result.mise_totale) * 100

        return result

    def _calculate_simple(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Simple"""
        for pred in predictions[:3]:  # Max 3 chevaux en Simple
            mise = result.mise_unitaire
            result.mise_totale += mise
            
            for rapport in rapports:
                if pred in rapport['numeros']:
                    # Gagnant
                    if pred == arrivee[0] and 'rapport_gagnant' in rapport:
                        gain = float(rapport['rapport_gagnant']) * mise
                        result.gains_bruts += gain
                        result.details.append(f"Simple gagnant n°{pred}: {gain:.2f}€")
                    
                    # Placé
                    if pred in arrivee[:3] and 'rapport_1' in rapport:
                        gain = float(rapport['rapport_1']) * mise
                        result.gains_bruts += gain
                        result.details.append(f"Simple placé n°{pred}: {gain:.2f}€")
        
        return result

    def _calculate_couple(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Couplé"""
        for i, pred1 in enumerate(predictions[:-1]):
            for pred2 in predictions[i+1:]:
                mise = result.mise_unitaire
                result.mise_totale += mise
                
                pred_set = {pred1, pred2}
                for rapport in rapports:
                    nums_set = set(rapport['numeros'])
                    if pred_set == nums_set:
                        # Gagnant
                        if 'rapport_gagnant' in rapport:
                            gain = float(rapport['rapport_gagnant']) * mise
                            result.gains_bruts += gain
                            result.details.append(f"Couplé gagnant {pred_set}: {gain:.2f}€")
                        
                        # Placé
                        if 'rapport_1' in rapport:
                            gain = float(rapport['rapport_1']) * mise
                            result.gains_bruts += gain
                            result.details.append(f"Couplé placé {pred_set}: {gain:.2f}€")
        
        return result

    def _calculate_deux_sur_quatre(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari 2 sur 4"""
        for i, pred1 in enumerate(predictions[:-1]):
            for pred2 in predictions[i+1:]:
                mise = result.mise_unitaire
                result.mise_totale += mise
                
                pred_set = {pred1, pred2}
                arrivee_4 = set(arrivee[:4])
                
                if len(pred_set & arrivee_4) >= 2:
                    for rapport in rapports:
                        if 'rapport_1' in rapport:
                            gain = float(rapport['rapport_1']) * (mise / 3.0)  # Divise par 3 car mise de base = 3€
                            result.gains_bruts += gain
                            result.details.append(f"2 sur 4 {pred_set}: {gain:.2f}€")
        
        return result

    def _calculate_trio(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Trio"""
        for i, pred1 in enumerate(predictions[:-2]):
            for j, pred2 in enumerate(predictions[i+1:-1]):
                for pred3 in predictions[i+j+2:]:
                    mise = result.mise_unitaire
                    result.mise_totale += mise
                    
                    pred_set = {pred1, pred2, pred3}
                    for rapport in rapports:
                        if set(rapport['numeros']) == pred_set and 'rapport_1' in rapport:
                            gain = float(rapport['rapport_1']) * mise
                            result.gains_bruts += gain
                            result.details.append(f"Trio {pred_set}: {gain:.2f}€")
        
        return result

    def _calculate_tierce(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Tiercé"""
        for i, pred1 in enumerate(predictions[:-2]):
            for j, pred2 in enumerate(predictions[i+1:-1]):
                for pred3 in predictions[i+j+2:]:
                    mise = result.mise_unitaire
                    result.mise_totale += mise
                    
                    pred_list = [pred1, pred2, pred3]
                    for rapport in rapports:
                        if rapport['numeros'] == pred_list:
                            # Ordre
                            if 'rapport_1' in rapport:
                                gain = float(rapport['rapport_1']) * mise
                                result.gains_bruts += gain
                                result.details.append(f"Tiercé ordre {pred_list}: {gain:.2f}€")
                            
                            # Désordre
                            if 'rapport_2' in rapport:
                                gain = float(rapport['rapport_2']) * mise
                                result.gains_bruts += gain
                                result.details.append(f"Tiercé désordre {pred_list}: {gain:.2f}€")
        
        return result

    def _calculate_quarte(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Quarté"""
        for rapport in rapports:
            mise = result.mise_unitaire
            nums = rapport['numeros']
            sous_type = rapport.get('sous_type', '')
            
            if sous_type == 'Ordre' and 'rapport_1' in rapport:
                gain = float(rapport['rapport_1']) * (mise / 1.3)  # Ajuste pour mise de 1.30€
                result.gains_bruts += gain
                result.details.append(f"Quarté ordre {nums}: {gain:.2f}€")
            
            elif sous_type == 'Désordre' and 'rapport_1' in rapport:
                gain = float(rapport['rapport_1']) * (mise / 1.3)
                result.gains_bruts += gain
                result.details.append(f"Quarté désordre {nums}: {gain:.2f}€")
            
            elif sous_type == 'Bonus 3' and 'rapport_1' in rapport:
                gain = float(rapport['rapport_1']) * (mise / 1.3)
                result.gains_bruts += gain
                result.details.append(f"Quarté bonus 3 {nums}: {gain:.2f}€")
            
            result.mise_totale += mise
        
        return result

    def _calculate_quinte(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Quinté"""
        for rapport in rapports:
            mise = result.mise_unitaire
            nums = rapport['numeros']
            sous_type = rapport.get('sous_type', '')
            
            if 'rapport_1' in rapport:
                gain = float(rapport['rapport_1']) * (mise / 2.0)  # Ajuste pour mise de 2€
                result.gains_bruts += gain
                result.details.append(f"Quinté {sous_type} {nums}: {gain:.2f}€")
            
            result.mise_totale += mise
        
        return result

    def _calculate_multi(self, predictions: List[str], arrivee: List[str], rapports: List[Dict], result: BettingResult) -> BettingResult:
        """Calcule les gains pour le pari Multi"""
        if not rapports:
            return result
            
        pred_set = set(predictions[:4])
        arrivee_4 = set(arrivee[:4])
        chevaux_trouves = len(pred_set & arrivee_4)
        
        for rapport in rapports:
            if 'rapport_1' in rapport:
                mise = result.mise_unitaire
                result.mise_totale += mise
                
                gain = float(rapport['rapport_1']) * (mise / 3.0)  # Ajuste pour mise de base
                result.gains_bruts += gain
                result.details.append(f"Multi {chevaux_trouves} chevaux: {gain:.2f}€")
        
        return result
