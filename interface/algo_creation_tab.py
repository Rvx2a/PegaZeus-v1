import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import sys
import os
import importlib.util
import tempfile
import ast
import json
from pathlib import Path

class AlgoCreationTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setup_ui()

    def setup_ui(self):
        """Initialise l'interface utilisateur"""
        # Panneau principal divisé en deux
        self.pack(fill='both', expand=True)
        
        # Panneau gauche (éditeur de code)
        left_panel = ttk.Frame(self)
        left_panel.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        # Zone d'édition du code
        editor_frame = ttk.LabelFrame(left_panel, text="Éditeur d'algorithme")
        editor_frame.pack(fill='both', expand=True)
        
        self.code_editor = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, 
                                                   width=80, height=30,
                                                   font=('Courier', 10))
        self.code_editor.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Template de base pour l'algorithme
        self.code_editor.insert('1.0', self.get_algorithm_template())
        
        # Boutons d'action
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="Sauvegarder", 
                  command=self.save_algorithm).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Tester", 
                  command=self.test_algorithm).pack(side='left', padx=5)
        
        # Panneau droit (aide et résultats)
        right_panel = ttk.Frame(self)
        right_panel.pack(side='right', fill='both', expand=False, padx=5, pady=5)
        
        # Documentation
        doc_frame = ttk.LabelFrame(right_panel, text="Documentation")
        doc_frame.pack(fill='both', expand=False)
        
        doc_text = scrolledtext.ScrolledText(doc_frame, wrap=tk.WORD, 
                                           width=40, height=15)
        doc_text.pack(fill='both', expand=True, padx=5, pady=5)
        doc_text.insert('1.0', self.get_documentation())
        doc_text.configure(state='disabled')
        
        # Résultats des tests
        test_frame = ttk.LabelFrame(right_panel, text="Résultats des tests")
        test_frame.pack(fill='both', expand=True)
        
        self.test_results = scrolledtext.ScrolledText(test_frame, wrap=tk.WORD)
        self.test_results.pack(fill='both', expand=True, padx=5, pady=5)

    def get_algorithm_template(self):
        """Retourne un template de base pour l'algorithme"""
        return '''from algos.base_algo import AlgoBase
from typing import List, Dict

class NewAlgorithm(AlgoBase):
    """Description de votre algorithme"""
    
    @property
    def name(self) -> str:
        return "NomAlgorithme"
        
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
'''

    def get_documentation(self):
        """Retourne la documentation pour la création d'algorithmes"""
        return """Création d'algorithmes - Guide

1. Structure de base
   - Hériter de AlgoBase
   - Implémenter name et analyze_race
   - Retourner max 5 chevaux

2. Données disponibles dans race :
   - race['partants']: Liste des partants
   - race['infos_course']: Infos course
        - type_course
        - distance
        - corde
        - piste
        - meteo
   - partant['numero']: Numéro du cheval
   - partant['coeff_forme_cheval']: 0-10
   - partant['appetence_distance']: 0-10
   - etc.

3. Méthodes utiles
   filter_valid_runners(): Filtre les non-partants
   get_odds(): Récupère les cotes
   
4. Bonnes pratiques
   - Gérer les erreurs avec try/except
   - Documenter le code
   - Optimiser les calculs
   - Tester les résultats

5. Conseils d'algorithme
   - Utiliser les coefficients de forme
   - Prendre en compte les cotes
   - Vérifier les appétences
   - Combiner plusieurs facteurs
   - Normaliser les scores"""

    def save_algorithm(self):
        """Sauvegarde l'algorithme"""
        try:
            # Récupère le code
            code = self.code_editor.get("1.0", tk.END)
            
            # Vérifie la syntaxe Python
            try:
                ast.parse(code)
            except SyntaxError as e:
                self.test_results.delete('1.0', tk.END)
                self.test_results.insert('1.0', f"Erreur de syntaxe: {str(e)}\n")
                return
            
            # Extrait le nom de la classe
            try:
                tree = ast.parse(code)
                class_def = next(node for node in ast.walk(tree) 
                               if isinstance(node, ast.ClassDef))
                class_name = class_def.name
            except:
                self.test_results.delete('1.0', tk.END)
                self.test_results.insert('1.0', "Erreur: Impossible de trouver la classe d'algorithme\n")
                return
            
            # Sauvegarde dans un fichier
            filename = f"algo_{class_name.lower()}.py"
            filepath = str(Path(__file__).parent.parent / 'algos' / filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(code)
                
            self.test_results.delete('1.0', tk.END)
            self.test_results.insert('1.0', f"Algorithme sauvegardé dans {filename}\n")
            
        except Exception as e:
            self.test_results.delete('1.0', tk.END)
            self.test_results.insert('1.0', f"Erreur lors de la sauvegarde: {str(e)}\n")

    def test_algorithm(self):
        """Teste l'algorithme sur des données réelles"""
        try:
            # Récupère le code
            code = self.code_editor.get("1.0", tk.END)
            
            # Crée un fichier temporaire pour le test
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                tf.write(code)
                temp_path = tf.name
                
            try:
                # Charge le module temporaire
                spec = importlib.util.spec_from_file_location("temp_algo", temp_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Trouve la classe d'algorithme
                algo_class = next(obj for name, obj in module.__dict__.items() 
                                if isinstance(obj, type) and name != 'AlgoBase' 
                                and issubclass(obj, module.AlgoBase))
                
                # Instancie l'algorithme
                algo = algo_class()
                
                # Charge quelques courses de test
                db_path = Path(__file__).parent.parent / 'races_database.json'
                with open(db_path, 'r', encoding='utf-8') as f:
                    database = json.load(f)
                    
                # Test sur les 3 premières courses
                self.test_results.delete('1.0', tk.END)
                self.test_results.insert('1.0', f"Test de l'algorithme {algo.name}\n\n")
                
                test_races = list(database['races'].items())[:3]
                for race_id, race in test_races:
                    try:
                        predictions = algo.analyze_race(race)
                        self.test_results.insert('end', 
                            f"Course {race['infos_course']['nom']}:\n"
                            f"Prédictions: {predictions}\n"
                            f"Arrivée réelle: {race['infos_course'].get('arrivee', [])}\n\n")
                    except Exception as e:
                        self.test_results.insert('end', 
                            f"Erreur sur la course {race_id}: {str(e)}\n\n")
                        
            finally:
                # Nettoie le fichier temporaire
                os.unlink(temp_path)
                
        except Exception as e:
            self.test_results.delete('1.0', tk.END)
            self.test_results.insert('1.0', f"Erreur lors du test: {str(e)}\n")
