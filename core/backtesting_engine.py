from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from algos.base_algo import AlgoBase as Strategy
from .betting_calculator import BettingCalculator  # Nouveau

@dataclass
class BacktestingConfig:
    odds_type: str = 'pmu'
    operateur: str = 'PMU'  # Ajouté
    paris_selectionnes: Optional[List[str]] = None  # Ajouté
    type_course: Optional[List[str]] = None
    distance_min: Optional[int] = None
    distance_max: Optional[int] = None
    allocation_min: Optional[float] = None
    allocation_max: Optional[float] = None
    piste: Optional[List[str]] = None
    corde: Optional[List[str]] = None
    location: Optional[List[str]] = None
    nb_partants_min: Optional[int] = None
    nb_partants_max: Optional[int] = None

    def __post_init__(self):
        if self.type_course is None:
            self.type_course = []
        if self.piste is None:
            self.piste = []
        if self.corde is None:
            self.corde = []
        if self.location is None:
            self.location = []

class BacktestingResult:
    """Résultats du backtesting"""
    def __init__(self):
        self.total_races = 0
        self.total_bets = 0.0
        self.total_returns = 0.0
        self.roi = 0.0
        self.races_details = []
        self.betting_results = {}  # Ajouté pour stocker les résultats par type de pari

    def add_race(self, race_id: str, predictions: List[int], 
                arrival: List[int], betting_results: Dict):
        """Ajoute une course aux résultats"""
        if not predictions or not arrival:
            return

        self.total_races += 1
        
        # Ajoute les résultats de paris
        for bet_type, result in betting_results.items():
            if bet_type not in self.betting_results:
                self.betting_results[bet_type] = {
                    'total_bets': 0.0,
                    'total_returns': 0.0,
                    'roi': 0.0,
                    'winning_races': 0
                }
            
            # Met à jour les totaux
            self.betting_results[bet_type]['total_bets'] += result.mise_totale
            self.betting_results[bet_type]['total_returns'] += result.gains_bruts
            if result.gains_bruts > result.mise_totale:
                self.betting_results[bet_type]['winning_races'] += 1
            
            # Calcule le ROI
            total_bets = self.betting_results[bet_type]['total_bets']
            total_returns = self.betting_results[bet_type]['total_returns']
            if total_bets > 0:
                self.betting_results[bet_type]['roi'] = \
                    ((total_returns - total_bets) / total_bets) * 100

        # Ajoute les détails de la course
        self.races_details.append({
            'race_id': race_id,
            'predictions': predictions,
            'arrival': arrival,
            'betting_results': betting_results
        })

    def get_summary(self) -> Dict:
        """Retourne un résumé des résultats"""
        total_bets = sum(bet['total_bets'] for bet in self.betting_results.values())
        total_returns = sum(bet['total_returns'] for bet in self.betting_results.values())
        
        return {
            'total_races': self.total_races,
            'total_bets': round(total_bets, 2),
            'total_returns': round(total_returns, 2),
            'roi': round(((total_returns - total_bets) / total_bets * 100) if total_bets > 0 else 0, 2),
            'betting_results': {
                bet_type: {
                    'total_bets': round(results['total_bets'], 2),
                    'total_returns': round(results['total_returns'], 2),
                    'roi': round(results['roi'], 2),
                    'winning_races': results['winning_races']
                }
                for bet_type, results in self.betting_results.items()
            }
        }

class BacktestingEngine:
    """Moteur de backtesting"""
    def __init__(self):
        self.results = BacktestingResult()
        self.calculator = BettingCalculator()  # Nouveau

    def run(self, races: Dict[str, Dict], strategy: Strategy, 
            config: BacktestingConfig) -> BacktestingResult:
        """Exécute le backtesting avec les paramètres donnés"""
        self.results = BacktestingResult()
        self.calculator.operateur = config.operateur
        
        for race_id, race in races.items():
            try:
                if not validate_race(race, config):
                    continue
                    
                predictions = strategy.analyze_race(race)
                if not predictions:
                    continue
                    
                arrival = [int(x) for x in race['infos_course']['arrivee']]
                
                # Calcule les gains pour tous les paris sélectionnés
                betting_results = self.calculator.calculate_course_gains(
                    race,
                    predictions,
                    config.paris_selectionnes
                )
                
                self.results.add_race(race_id, predictions, arrival, betting_results)
                
            except Exception as e:
                print(f"Erreur lors du traitement de la course {race_id}: {e}")
                continue
                
        return self.results

def validate_race(race: Dict, config: BacktestingConfig) -> bool:
    """Vérifie si une course correspond aux critères"""
    try:
        # Type de course
        if config.type_course and race['infos_course']['type_course'] not in config.type_course:
            return False
            
        # Distance
        if race['infos_course'].get('distance'):
            distance = int(''.join(filter(str.isdigit, race['infos_course']['distance'])))
            if config.distance_min and distance < config.distance_min:
                return False
            if config.distance_max and distance > config.distance_max:
                return False
                
        # Allocation
        if race['infos_course'].get('allocation'):
            allocation = float(''.join(filter(str.isdigit, race['infos_course']['allocation'])))
            if config.allocation_min and allocation < config.allocation_min:
                return False
            if config.allocation_max and allocation > config.allocation_max:
                return False
                
        # Autres critères...
        return True
        
    except Exception as e:
        print(f"Erreur lors de la validation de la course: {e}")
        return False

    def get_odds_for_race(race: Dict, predictions: List[int], odds_type: str) -> Dict[str, float]:
        """Récupère les cotes pour une course"""
        odds = {}
        
        def parse_cote(cote_str: str) -> float:
            """Parse une cote avec gestion des NC"""
            if cote_str in ['NC', '', None]:
                return 0.0
            try:
                return float(str(cote_str).replace(',', '.'))
            except (ValueError, TypeError):
                return 0.0
        
        for i, pred in enumerate(predictions[:3], 1):
            try:
                runner = next((r for r in race['partants'] if r.get('numero') != 'NP' 
                             and int(r['numero']) == pred), None)
                if runner:
                    # Utilise la fonction de parsing sécurisée
                    cote = parse_cote(runner.get(odds_type))
                    if cote > 0:
                        odds[f'win_{i}'] = cote
                        odds[f'place_{i}'] = cote * 0.25  # Estimation simplifiée
                    else:
                        odds[f'win_{i}'] = 0.0
                        odds[f'place_{i}'] = 0.0
                else:
                    odds[f'win_{i}'] = 0.0
                    odds[f'place_{i}'] = 0.0
                    
            except (ValueError, KeyError, TypeError):
                odds[f'win_{i}'] = 0.0
                odds[f'place_{i}'] = 0.0
                
        return odds

def run_backtest(races: Dict[str, Dict], strategy: Strategy, 
                config: BacktestingConfig) -> BacktestingResult:
    """Fonction utilitaire pour lancer un backtest"""
    engine = BacktestingEngine()
    return engine.run(races, strategy, config)
