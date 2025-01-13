from datetime import datetime
from typing import Dict, List
import pandas as pd
import numpy as np

class RaceAnalyzer:
    """Classe avancée pour analyser les données des courses"""
    def __init__(self, data):
        self.data = data
        self.runners = data['partants']
        self.race_info = data['infos_course']

    def analyze_race(self) -> Dict:
        """Analyse complète d'une course"""
        try:
            analysis = {
                'infos_course': self._analyze_race_info(),
                'partants': self._analyze_runners(),
                'performances': self._analyze_performance_trends(),
                'probabilites': self._calculate_probabilities(),
                'facteurs_cles': self._identify_key_factors(),
                'alertes': self._detect_anomalies(),
                'stats': self._calculate_statistics()
            }
            return analysis
        except Exception as e:
            print(f"Erreur lors de l'analyse: {str(e)}")
            return {}

    def _analyze_race_info(self) -> Dict:
        """Analyse les informations de base de la course"""
        info = {
            'nom': self.race_info.get('nom', ''),
            'type': self.race_info.get('type_course', ''),
            'distance': int(''.join(filter(str.isdigit, self.race_info.get('distance', '0')))),
            'piste': self.race_info.get('piste', ''),
            'corde': self.race_info.get('corde', ''),
            'meteo': self.race_info.get('meteo', {}),
            'difficulte': self._evaluate_difficulty()
        }
        return info

    def _analyze_runners(self) -> List[Dict]:
        """Analyse détaillée de chaque partant"""
        analyzed_runners = []
        for runner in self.runners:
            analysis = {
                'numero': runner['numero'],
                'nom': runner['nom_cheval'],
                'cotes': self._analyze_odds(runner),
                'forme': self._analyze_form(runner),
                'stats': self._get_runner_stats(runner),
                'risques': self._evaluate_risks(runner),
                'score_final': self._calculate_final_score(runner)
            }
            analyzed_runners.append(analysis)
        return analyzed_runners

    def _analyze_performance_trends(self) -> Dict:
        """Analyse les tendances de performance"""
        trends = {
            'forme_generale': self._analyze_general_form(),
            'evolution_cotes': self._analyze_odds_evolution(),
            'impact_meteo': self._analyze_weather_impact(),
            'tendances_hippodrome': self._analyze_track_trends()
        }
        return trends

    def _calculate_probabilities(self) -> Dict:
        """Calcule les probabilités de victoire"""
        probabilities = {}
        total_score = sum(r['score_final'] for r in self._analyze_runners())
        
        for runner in self._analyze_runners():
            if total_score > 0:
                prob = runner['score_final'] / total_score
                probabilities[runner['numero']] = {
                    'victoire': prob,
                    'place': min(prob * 1.5, 1.0),
                    'valeur': self._calculate_value(prob, runner['cotes']['pmu'])
                }
        return probabilities

    def _identify_key_factors(self) -> Dict:
        """Identifie les facteurs clés de la course"""
        factors = {
            'terrain': self._analyze_track_conditions(),
            'rythme': self._analyze_pace(),
            'classe': self._analyze_class_level(),
            'tactique': self._suggest_tactics()
        }
        return factors

    def _detect_anomalies(self) -> List[Dict]:
        """Détecte les anomalies et points d'attention"""
        anomalies = []
        
        # Vérification des cotes anormales
        odds_anomalies = self._check_odds_anomalies()
        if odds_anomalies:
            anomalies.extend(odds_anomalies)
            
        # Vérification des changements de forme
        form_changes = self._check_form_changes()
        if form_changes:
            anomalies.extend(form_changes)
            
        # Vérification des conditions particulières
        special_conditions = self._check_special_conditions()
        if special_conditions:
            anomalies.extend(special_conditions)
            
        return anomalies

    def _calculate_statistics(self) -> Dict:
        """Calcule les statistiques globales"""
        stats = {
            'nombre_partants': len(self.runners),
            'moyenne_cotes': self._calculate_average_odds(),
            'ecart_type_cotes': self._calculate_odds_std(),
            'indice_competitivite': self._calculate_competitiveness(),
            'correlations': self._calculate_correlations()
        }
        return stats

    def _evaluate_difficulty(self) -> float:
        """Évalue la difficulté de la course"""
        try:
            factors = {
                'nombre_partants': len(self.runners) / 20,  # Normalisé sur 20 partants
                'distance': int(''.join(filter(str.isdigit, self.race_info.get('distance', '0')))) / 3000,
                'allocation': float(''.join(filter(str.isdigit, self.race_info.get('allocation', '0')))) / 100000,
                'competitivite': self._calculate_competitiveness()
            }
            
            weights = {
                'nombre_partants': 0.25,
                'distance': 0.25,
                'allocation': 0.25,
                'competitivite': 0.25
            }
            
            difficulty = sum(factor * weights[key] for key, factor in factors.items())
            return min(max(difficulty, 0), 1)  # Normalisé entre 0 et 1
            
        except Exception as e:
            print(f"Erreur lors de l'évaluation de la difficulté: {str(e)}")
            return 0.5

    def _analyze_odds(self, runner: Dict) -> Dict:
        """Analyse les cotes du partant"""
        def parse_cote(cote_str):
            """Parse une cote en gérant NC"""
            if cote_str in ['NC', '', None]:
                return None
            try:
                return float(str(cote_str).replace(',', '.'))
            except (ValueError, TypeError):
                return None

        odds = {
            'pmu': parse_cote(runner.get('pmu')),
            'pmu_fr': parse_cote(runner.get('pmu_fr')),
            'zeturf': parse_cote(runner.get('zeturf')),
            'evolution': {
                'pmu': parse_cote(runner.get('pmu_evolution')),
                'pmu_fr': parse_cote(runner.get('pmu_fr_evolution')),
                'zeturf': parse_cote(runner.get('zeturf_evolution'))
            }
        }
        
        # Calcul du consensus uniquement avec les cotes disponibles
        valid_odds = [v for v in [odds['pmu'], odds['pmu_fr'], odds['zeturf']] 
                     if v is not None and v < 100]
        odds['consensus'] = np.mean(valid_odds) if valid_odds else None
        
        return odds

    def _analyze_form(self, runner: Dict) -> Dict:
        """Analyse la forme du partant"""
        form = {
            'musique': self._parse_musique(runner.get('musique', '')),
            'coefficients': {
                'forme_cheval': float(runner.get('coeff_forme_cheval', 0)),
                'forme_jockey': float(runner.get('coeff_forme_jockey', 0)),
                'forme_entraineur': float(runner.get('coeff_forme_entraineur', 0))
            },
            'tendance': self._calculate_form_trend(runner),
            'regularite': self._calculate_regularity(runner)
        }
        return form

    def _get_runner_stats(self, runner: Dict) -> Dict:
        """Récupère les statistiques du partant"""
        stats = {
            'victoires': self._count_wins(runner),
            'places': self._count_places(runner),
            'gains': float(runner.get('gains', 0)),
            'performances': {
                'distance': float(runner.get('appetence_distance', 0)),
                'piste': float(runner.get('appetence_sol', 0)),
                'hippodrome': float(runner.get('appetence_hippodrome', 0))
            }
        }
        return stats

    def _evaluate_risks(self, runner: Dict) -> List[str]:
        """Évalue les risques liés au partant"""
        risks = []
        
        # Vérification de la forme
        if float(runner.get('coeff_forme_cheval', 0)) < 5:
            risks.append("Forme douteuse")
            
        # Vérification des appétences
        if float(runner.get('appetence_distance', 0)) < 5:
            risks.append("Distance non optimale")
        if float(runner.get('appetence_sol', 0)) < 5:
            risks.append("Terrain non optimal")
            
        # Vérification des cotes
        try:
            cote = float(str(runner.get('pmu', '999')).replace(',', '.'))
            if cote > 30:
                risks.append("Outsider prononcé")
        except ValueError:
            risks.append("Cote non disponible")
            
        return risks

    def _calculate_final_score(self, runner: Dict) -> float:
        """Calcule le score final du partant"""
        try:
            # Coefficients de forme (40%)
            forme_score = (
                float(runner.get('coeff_forme_cheval', 0)) * 0.2 +
                float(runner.get('coeff_forme_jockey', 0)) * 0.1 +
                float(runner.get('coeff_forme_entraineur', 0)) * 0.1
            )
            
            # Appétences (30%)
            appetence_score = (
                float(runner.get('appetence_distance', 0)) * 0.1 +
                float(runner.get('appetence_sol', 0)) * 0.1 +
                float(runner.get('appetence_hippodrome', 0)) * 0.1
            )
            
            # Cote (20%)
            try:
                cote = float(str(runner.get('pmu', '999')).replace(',', '.'))
                odds_score = (100 - min(cote, 100)) / 100 * 0.2
            except ValueError:
                odds_score = 0
                
            # Musique récente (10%)
            musique_score = self._calculate_musique_score(runner) * 0.1
            
            return forme_score + appetence_score + odds_score + musique_score
            
        except Exception as e:
            print(f"Erreur lors du calcul du score final: {str(e)}")
            return 0

    def _calculate_competitiveness(self) -> float:
        """Calcule l'indice de compétitivité de la course"""
        try:
            # Récupère les cotes PMU
            cotes = []
            for runner in self.runners:
                try:
                    cote = float(str(runner.get('pmu', '999')).replace(',', '.'))
                    if cote < 100:  # Ignore les très gros outsiders
                        cotes.append(cote)
                except ValueError:
                    continue
                    
            if not cotes:
                return 0.5
                
            # Calcule la moyenne et l'écart-type
            mean = np.mean(cotes)
            std = np.std(cotes)
            
            # Calcule le coefficient de variation (écart-type / moyenne)
            cv = std / mean if mean > 0 else 1
            
            # Normalise entre 0 et 1 (plus le CV est faible, plus la course est compétitive)
            competitiveness = 1 - min(cv, 1)
            
            return competitiveness
            
        except Exception as e:
            print(f"Erreur lors du calcul de la compétitivité: {str(e)}")
            return 0.5

    def _analyze_pace(self) -> Dict:
        """Analyse le rythme probable de la course"""
        # Implémentation à compléter
        return {}

    def _suggest_tactics(self) -> List[str]:
        """Suggère des tactiques de jeu"""
        suggestions = []
        
        # Analyse de la compétitivité
        competitiveness = self._calculate_competitiveness()
        if competitiveness > 0.8:
            suggestions.append("Course très ouverte: privilégier les jeux de combinaison")
        elif competitiveness < 0.4:
            suggestions.append("Course sélective: se concentrer sur les favoris")
            
        # Analyse des cotes
        cotes = []
        for runner in self.runners:
            try:
                cote = float(str(runner.get('pmu', '999')).replace(',', '.'))
                if cote < 100:
                    cotes.append(cote)
            except ValueError:
                continue
                
        if cotes:
            mean_odds = np.mean(cotes)
            if mean_odds > 15:
                suggestions.append("Cotes élevées: envisager des jeux de combinaison")
            elif mean_odds < 8:
                suggestions.append("Cotes basses: privilégier les jeux simples")
                
        return suggestions

    def _calculate_correlations(self) -> Dict:
        """Calcule les corrélations entre différentes variables"""
        correlations = {}
        
        # Prépare les données
        data = []
        for runner in self.runners:
            try:
                row = {
                    'cote': float(str(runner.get('pmu', '999')).replace(',', '.')),
                    'forme': float(runner.get('coeff_forme_cheval', 0)),
                    'appetence_distance': float(runner.get('appetence_distance', 0)),
                    'appetence_sol': float(runner.get('appetence_sol', 0))
                }
                data.append(row)
            except ValueError:
                continue
                
        if data:
            df = pd.DataFrame(data)
            corr_matrix = df.corr()
            
            # Extrait les corrélations pertinentes
            correlations = {
                'cote_forme': corr_matrix.loc['cote', 'forme'],
                'cote_distance': corr_matrix.loc['cote', 'appetence_distance'],
                'cote_sol': corr_matrix.loc['cote', 'appetence_sol']
            }
            
        return correlations

    def _parse_musique(self, musique: str) -> List[Dict]:
        """Parse la musique d'un cheval"""
        results = []
        if not musique:
            return results
            
        # Nettoie la musique
        musique = musique.replace('(', '').replace(')', '')
        
        for char in musique:
            if char.isdigit():
                results.append({
                    'position': int(char),
                    'type': 'place' if int(char) <= 3 else 'autre'
                })
            elif char in ['D', 'A', 'T']:
                results.append({
                    'position': char,
                    'type': 'disqualification' if char == 'D' else 'arrêt' if char == 'A' else 'tombé'
                })
                
        return results

    def _calculate_form_trend(self, runner: Dict) -> str:
        """Calcule la tendance de forme"""
        musique = self._parse_musique(runner.get('musique', ''))
        if not musique:
            return "inconnue"
            
        # Prend les 5 derniers résultats
        recent = musique[:5]
        if not recent:
            return "inconnue"
            
        # Calcule le score moyen récent
        scores = []
        for result in recent:
            if isinstance(result['position'], int):
                scores.append(max(10 - result['position'], 0))
            else:
                scores.append(0)
                
        if not scores:
            return "inconnue"
            
        avg = sum(scores) / len(scores)
        if avg > 7:
            return "excellente"
        elif avg > 5:
            return "bonne"
        elif avg > 3:
            return "moyenne"
        else:
            return "médiocre"

    def _calculate_regularity(self, runner: Dict) -> float:
        """Calcule l'indice de régularité"""
        musique = self._parse_musique(runner.get('musique', ''))
        if not musique:
            return 0
            
        # Ne considère que les positions numériques
        positions = [r['position'] for r in musique if isinstance(r['position'], int)]
        if not positions:
            return 0
            
        # Calcule l'écart-type des positions
        std = np.std(positions) if len(positions) > 1 else 0
        
        # Normalise entre 0 et 1 (plus l'écart-type est faible, plus le cheval est régulier)
        regularity = max(0, 1 - (std / 10))
        
        return regularity

    def _calculate_odds_consensus(self, runner: Dict) -> float:
        """Calcule le consensus des cotes"""
        odds = []
        for key in ['pmu', 'pmu_fr', 'zeturf']:
            try:
                value = float(str(runner.get(key, '999')).replace(',', '.'))
                if value < 100:
                    odds.append(value)
            except ValueError:
                continue
                
        if not odds:
            return 999
            
        return np.mean(odds)

    def _analyze_track_conditions(self) -> Dict:
        """Analyse les conditions de piste"""
        conditions = {
            'type_piste': self.race_info.get('piste', ''),
            'meteo': self.race_info.get('meteo', {}),
            'impact': self._evaluate_track_impact()
        }
        return conditions

    def _evaluate_track_impact(self) -> Dict:
        """Évalue l'impact des conditions de piste"""
        impact = {
            'general': 'neutre',
            'avantage': [],
            'desavantage': []
        }
        
        # Analyse l'impact de la météo
        meteo = self.race_info.get('meteo', {})
        if 'pluie' in meteo.get('conditions', '').lower():
            impact['general'] = 'significatif'
            for runner in self.runners:
                if float(runner.get('appetence_sol', 5)) > 7:
                    impact['avantage'].append(runner['numero'])
                elif float(runner.get('appetence_sol', 5)) < 3:
                    impact['desavantage'].append(runner['numero'])
                    
        # Analyse l'impact de la piste
        piste = self.race_info.get('piste', '')
        if any(surface in piste.lower() for surface in ['herbe', 'sable', 'machefer']):
            impact['general'] = 'significatif'
            
        return impact

    def _analyze_class_level(self) -> Dict:
        """Analyse le niveau de la course"""
        allocation = float(''.join(filter(str.isdigit, self.race_info.get('allocation', '0'))))
        
        level = {
            'allocation': allocation,
            'niveau': 'standard',
            'denivele': self._calculate_class_gap()
        }
        
        if allocation > 50000:
            level['niveau'] = 'élevé'
        elif allocation > 25000:
            level['niveau'] = 'bon'
        elif allocation < 10000:
            level['niveau'] = 'modeste'
            
        return level

    def _calculate_class_gap(self) -> float:
        """Calcule l'écart de niveau entre les partants"""
        gains = []
        for runner in self.runners:
            try:
                gain = float(runner.get('gains', 0))
                if gain > 0:
                    gains.append(gain)
            except ValueError:
                continue
                
        if not gains:
            return 0
            
        return (max(gains) - min(gains)) / max(gains)

    def _check_odds_anomalies(self) -> List[Dict]:
        """Détecte les anomalies dans les cotes"""
        anomalies = []
        
        for runner in self.runners:
            odds = []
            for key in ['pmu', 'pmu_fr', 'zeturf']:
                try:
                    value = float(str(runner.get(key, '999')).replace(',', '.'))
                    if value < 100:
                        odds.append(value)
                except ValueError:
                    continue
                    
            if len(odds) >= 2:
                mean = np.mean(odds)
                std = np.std(odds)
                cv = std / mean if mean > 0 else 0
                
                if cv > 0.3:  # Plus de 30% d'écart relatif
                    anomalies.append({
                        'type': 'disparité_cotes',
                        'numero': runner['numero'],
                        'description': f"Forte disparité des cotes ({cv:.2f})",
                        'severity': 'haute' if cv > 0.5 else 'moyenne'
                    })
                    
        return anomalies

    def _check_form_changes(self) -> List[Dict]:
        """Détecte les changements significatifs de forme"""
        changes = []
        
        for runner in self.runners:
            musique = self._parse_musique(runner.get('musique', ''))
            if len(musique) >= 3:
                recent = [r for r in musique[:3] if isinstance(r['position'], int)]
                older = [r for r in musique[3:6] if isinstance(r['position'], int)]
                
                if recent and older:
                    recent_avg = sum(r['position'] for r in recent) / len(recent)
                    older_avg = sum(r['position'] for r in older) / len(older)
                    
                    diff = abs(recent_avg - older_avg)
                    if diff > 5:
                        changes.append({
                            'type': 'changement_forme',
                            'numero': runner['numero'],
                            'description': 'Amélioration' if recent_avg < older_avg else 'Régression',
                            'severity': 'haute' if diff > 8 else 'moyenne'
                        })
                        
        return changes

    def _check_special_conditions(self) -> List[Dict]:
        """Détecte les conditions particulières"""
        conditions = []
        
        # Vérification des conditions météo
        meteo = self.race_info.get('meteo', {})
        if any(cond in meteo.get('conditions', '').lower() 
               for cond in ['orage', 'neige', 'brouillard']):
            conditions.append({
                'type': 'meteo_extreme',
                'description': f"Conditions météo difficiles: {meteo.get('conditions')}",
                'severity': 'haute'
            })
            
        # Vérification de la température
        try:
            temp = float(meteo.get('temperature', '20').replace('°', ''))
            if temp < 5 or temp > 30:
                conditions.append({
                    'type': 'temperature_extreme',
                    'description': f"Température extrême: {temp}°C",
                    'severity': 'moyenne'
                })
        except ValueError:
            pass
            
        return conditions

    def _calculate_value(self, probability: float, odds: float) -> float:
        """Calcule la valeur d'une cote"""
        try:
            if probability <= 0 or odds <= 0:
                return 0
                
            # La valeur est le ratio entre la probabilité réelle et la probabilité implicite des cotes
            implied_prob = 1 / odds
            value = probability / implied_prob - 1
            
            return value
            
        except Exception as e:
            print(f"Erreur lors du calcul de la valeur: {str(e)}")
            return 0

    def _calculate_average_odds(self) -> float:
        """Calcule la moyenne des cotes"""
        odds = []
        for runner in self.runners:
            try:
                value = float(str(runner.get('pmu', '999')).replace(',', '.'))
                if value < 100:
                    odds.append(value)
            except ValueError:
                continue
                
        return np.mean(odds) if odds else 0

    def _calculate_odds_std(self) -> float:
        """Calcule l'écart-type des cotes"""
        odds = []
        for runner in self.runners:
            try:
                value = float(str(runner.get('pmu', '999')).replace(',', '.'))
                if value < 100:
                    odds.append(value)
            except ValueError:
                continue
                
        return np.std(odds) if len(odds) > 1 else 0
