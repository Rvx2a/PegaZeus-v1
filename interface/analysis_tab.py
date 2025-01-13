import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from pathlib import Path
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from core.analyzer import RaceAnalyzer

class AnalysisTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.setup_ui()
        # Charge la liste des courses
        self.load_race_list()
        
    def setup_ui(self):
        """Initialise l'interface utilisateur"""
        # Configuration du grid
        self.columnconfigure(0, weight=1)  # Colonne des filtres
        self.columnconfigure(1, weight=3)  # Colonne principale
        
        # === Panneau gauche (Filtres) ===
        left_panel = ttk.Frame(self)
        left_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        # Filtres de base
        filter_frame = ttk.LabelFrame(left_panel, text="Filtres")
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        # Type de course
        ttk.Label(filter_frame, text="Type de course:").pack(anchor='w', padx=5, pady=2)
        self.race_type = ttk.Combobox(filter_frame, values=['Tous', 'Plat', 'Obstacle', 'Trot'])
        self.race_type.pack(fill='x', padx=5, pady=2)
        
        # Distance
        ttk.Label(filter_frame, text="Distance:").pack(anchor='w', padx=5, pady=2)
        distance_frame = ttk.Frame(filter_frame)
        distance_frame.pack(fill='x', padx=5)
        self.distance_min = ttk.Entry(distance_frame, width=10)
        self.distance_min.pack(side='left')
        ttk.Label(distance_frame, text="-").pack(side='left', padx=2)
        self.distance_max = ttk.Entry(distance_frame, width=10)
        self.distance_max.pack(side='left')
        
        # Hippodrome
        ttk.Label(filter_frame, text="Hippodrome:").pack(anchor='w', padx=5, pady=2)
        self.track = ttk.Combobox(filter_frame)
        self.track.pack(fill='x', padx=5, pady=2)
        
        # Période
        ttk.Label(filter_frame, text="Période:").pack(anchor='w', padx=5, pady=2)
        period_frame = ttk.Frame(filter_frame)
        period_frame.pack(fill='x', padx=5)
        self.date_start = ttk.Entry(period_frame, width=10)
        self.date_start.pack(side='left')
        ttk.Label(period_frame, text="-").pack(side='left', padx=2)
        self.date_end = ttk.Entry(period_frame, width=10)
        self.date_end.pack(side='left')
        
        # Bouton d'application des filtres
        ttk.Button(filter_frame, text="Appliquer", command=self.apply_filters).pack(pady=10)
        
        # === Panneau central ===
        central_panel = ttk.Frame(self)
        central_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        # Notebook pour les différentes vues
        self.analysis_notebook = ttk.Notebook(central_panel)
        self.analysis_notebook.pack(fill='both', expand=True)
        
        # --- Onglet Statistiques Globales ---
        stats_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(stats_frame, text='Statistiques Globales')
        
        # Statistiques de base
        basic_stats = ttk.LabelFrame(stats_frame, text="Statistiques de base")
        basic_stats.pack(fill='x', padx=5, pady=5)
        
        # Grid pour les stats
        self.stats_labels = {}
        initial_stats = [
            ("nombre_courses", "Nombre de courses:", "0"),
            ("moyenne_partants", "Moyenne partants:", "0"),
            ("taux_favoris", "Taux favoris gagnants:", "0%"),
            ("roi_moyen", "ROI moyen:", "0%")
        ]
        
        for i, (key, label, value) in enumerate(initial_stats):
            ttk.Label(basic_stats, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='w')
            self.stats_labels[key] = ttk.Label(basic_stats, text=value)
            self.stats_labels[key].grid(row=i, column=1, padx=5, pady=2, sticky='w')
        
        # --- Onglet Graphiques ---
        graphs_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(graphs_frame, text='Graphiques')
        
        # Menu de sélection du graphique
        graph_selection = ttk.Frame(graphs_frame)
        graph_selection.pack(fill='x', padx=5, pady=5)
        ttk.Label(graph_selection, text="Type de graphique:").pack(side='left')
        self.graph_type = ttk.Combobox(graphs_frame, 
            values=['Distribution des cotes', 'Performance par hippodrome', 'ROI par type'])
        self.graph_type.pack(side='left', padx=5)
        ttk.Button(graph_selection, text="Générer", 
                  command=self.generate_graph).pack(side='left', padx=5)
        
        # Zone de graphique
        self.graph_frame = ttk.Frame(graphs_frame)
        self.graph_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # --- Onglet Analyse Détaillée ---
        detailed_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(detailed_frame, text='Analyse Détaillée')
        
        # Sélecteur de course
        race_selector = ttk.Frame(detailed_frame)
        race_selector.pack(fill='x', padx=5, pady=5)
        ttk.Label(race_selector, text="Course:").pack(side='left')
        self.race_selector = ttk.Combobox(race_selector)
        self.race_selector.pack(side='left', padx=5, fill='x', expand=True)
        ttk.Button(race_selector, text="Analyser", 
                  command=self.analyze_race).pack(side='left')
        
        # Résultats d'analyse
        self.analysis_text = scrolledtext.ScrolledText(detailed_frame, height=20)
        self.analysis_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # --- Onglet Corrélations ---
        correlations_frame = ttk.Frame(self.analysis_notebook)
        self.analysis_notebook.add(correlations_frame, text='Corrélations')
        
        # Sélection des variables
        var_selector = ttk.Frame(correlations_frame)
        var_selector.pack(fill='x', padx=5, pady=5)
        ttk.Label(var_selector, text="Variable 1:").pack(side='left')
        self.var1 = ttk.Combobox(var_selector, values=['Cote', 'Distance', 'Âge'])
        self.var1.pack(side='left', padx=5)
        ttk.Label(var_selector, text="Variable 2:").pack(side='left')
        self.var2 = ttk.Combobox(var_selector, values=['Cote', 'Distance', 'Âge'])
        self.var2.pack(side='left', padx=5)
        ttk.Button(var_selector, text="Calculer", 
                  command=self.calculate_correlation).pack(side='left', padx=5)
        
        # Zone de résultat
        self.correlation_result = scrolledtext.ScrolledText(correlations_frame, height=20)
        self.correlation_result.pack(fill='both', expand=True, padx=5, pady=5)

    def apply_filters(self):
        """Applique les filtres sélectionnés"""
        try:
            self.update_statistics()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'application des filtres: {str(e)}")

    def generate_graph(self):
        """Génère le graphique sélectionné"""
        try:
            # Efface le graphique existant
            for widget in self.graph_frame.winfo_children():
                widget.destroy()
            
            # Crée une nouvelle figure
            fig = Figure(figsize=(6, 4))
            ax = fig.add_subplot(111)
            
            graph_type = self.graph_type.get()
            if graph_type == 'Distribution des cotes':
                self.plot_odds_distribution(ax)
            elif graph_type == 'Performance par hippodrome':
                self.plot_track_performance(ax)
            elif graph_type == 'ROI par type':
                self.plot_roi_by_type(ax)
            
            # Ajoute le graphique au frame
            canvas = FigureCanvasTkAgg(fig, self.graph_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la génération du graphique: {str(e)}")

    def plot_odds_distribution(self, ax):
        """Trace la distribution des cotes"""
        # Implémentation à faire
        ax.set_title("Distribution des cotes")
        pass

    def plot_track_performance(self, ax):
        """Trace les performances par hippodrome"""
        # Implémentation à faire
        ax.set_title("Performance par hippodrome")
        pass

    def plot_roi_by_type(self, ax):
        """Trace le ROI par type de course"""
        # Implémentation à faire
        ax.set_title("ROI par type de course")
        pass

    def analyze_race(self):
        """Analyse détaillée de la course sélectionnée"""
        try:
            # Récupère la course sélectionnée
            selection = self.race_selector.get()
            if not selection:
                messagebox.showwarning("Sélection", "Veuillez sélectionner une course")
                return

            # Extrait l'ID de la course du format "Nom (ID)"
            race_id = selection.split('(')[-1].rstrip(')')
                
            # Charge les données
            with open('races_database.json', 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            if race_id not in database['races']:
                messagebox.showerror("Erreur", "Course introuvable")
                return
                
            # Crée l'analyseur et effectue l'analyse
            race_data = database['races'][race_id]
            analyzer = RaceAnalyzer(race_data)
            analysis = analyzer.analyze()
            
            # Affiche les résultats
            self.display_analysis_results(analysis)
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'analyse: {str(e)}")

    def display_analysis_results(self, analysis):
        """Affiche les résultats de l'analyse"""
        self.analysis_text.delete('1.0', tk.END)
        
        # Informations de course
        self.analysis_text.insert(tk.END, "=== INFORMATIONS COURSE ===\n\n")
        self.analysis_text.insert(tk.END, f"Course: {analysis['infos_course'].get('nom', 'N/A')}\n")
        self.analysis_text.insert(tk.END, f"Date: {analysis['infos_course'].get('date_course', 'N/A')}\n")
        self.analysis_text.insert(tk.END, f"Hippodrome: {analysis['infos_course'].get('hippodrome', 'N/A')}\n\n")
        
        # Statistiques
        self.analysis_text.insert(tk.END, "=== STATISTIQUES ===\n\n")
        stats = analysis['statistiques']
        self.analysis_text.insert(tk.END, f"Nombre de partants: {stats['nombre_partants']}\n")
        
        # Tendances
        self.analysis_text.insert(tk.END, "\n=== TENDANCES ===\n")
        tendances = analysis['tendances']
        for numero, data in tendances['musique_analysis'].items():
            self.analysis_text.insert(tk.END, f"\nCheval {numero}:\n")
            self.analysis_text.insert(tk.END, f"  Tendance: {data['trend']}\n")
            self.analysis_text.insert(tk.END, f"  Constance: {data['consistency']:.2f}\n")
        
        # Corrélations
        self.analysis_text.insert(tk.END, "\n=== CORRÉLATIONS ===\n")
        corr = analysis['correlations']
        for factor, data in corr.items():
            self.analysis_text.insert(tk.END, f"\n{factor}:\n")
            self.analysis_text.insert(tk.END, f"  Corrélation: {data['correlation']:.2f}\n")
            self.analysis_text.insert(tk.END, f"  Significance: {data['significance']}\n")

    def load_race_list(self):
        """Charge la liste des courses dans le sélecteur"""
        try:
            with open('races_database.json', 'r', encoding='utf-8') as f:
                database = json.load(f)
                
            # Prépare les courses
            races = []
            for race_id, race in database['races'].items():
                race_name = race['infos_course']['nom']
                races.append((race_id, race_name))
            
            # Trie par nom
            races.sort(key=lambda x: x[1])
            
            # Met à jour le combobox
            self.race_selector['values'] = [f"{race[1]} ({race[0]})" for race in races]
            
        except Exception as e:
            print(f"Erreur lors du chargement des courses: {e}")

    def calculate_correlation(self):
        """Calcule la corrélation entre les variables sélectionnées"""
        try:
            var1 = self.var1.get()
            var2 = self.var2.get()
            
            if not var1 or not var2:
                messagebox.showwarning("Sélection", "Veuillez sélectionner deux variables")
                return
                
            # Charge les données
            with open('races_database.json', 'r', encoding='utf-8') as f:
                database = json.load(f)
            
            # Prépare les données
            data = []
            for race in database['races'].values():
                for partant in race['partants']:
                    row = {}
                    # Extraire les valeurs selon les variables sélectionnées
                    if var1 == 'Cote':
                        row['var1'] = float(str(partant.get('pmu', '0')).replace(',', '.'))
                    elif var1 == 'Distance':
                        row['var1'] = int(''.join(filter(str.isdigit, race['infos_course'].get('distance', '0'))))
                    elif var1 == 'Âge':
                        row['var1'] = int(partant.get('age', 0))
                        
                    if var2 == 'Cote':
                        row['var2'] = float(str(partant.get('pmu', '0')).replace(',', '.'))
                    elif var2 == 'Distance':
                        row['var2'] = int(''.join(filter(str.isdigit, race['infos_course'].get('distance', '0'))))
                    elif var2 == 'Âge':
                        row['var2'] = int(partant.get('age', 0))
                        
                    data.append(row)
            
            # Calcule la corrélation
            df = pd.DataFrame(data)
            correlation = df['var1'].corr(df['var2'])
            
            # Affiche les résultats
            self.correlation_result.delete('1.0', tk.END)
            self.correlation_result.insert('1.0', f"=== Analyse de corrélation ===\n\n")
            self.correlation_result.insert('end', f"Variables : {var1} et {var2}\n")
            self.correlation_result.insert('end', f"Coefficient de corrélation : {correlation:.3f}\n\n")
            
            # Interprétation
            self.correlation_result.insert('end', "Interprétation :\n")
            if abs(correlation) < 0.3:
                self.correlation_result.insert('end', "Corrélation faible\n")
            elif abs(correlation) < 0.6:
                self.correlation_result.insert('end', "Corrélation modérée\n")
            else:
                self.correlation_result.insert('end', "Corrélation forte\n")
            
            if correlation > 0:
                self.correlation_result.insert('end', "Relation positive : Les variables évoluent dans le même sens\n")
            else:
                self.correlation_result.insert('end', "Relation négative : Les variables évoluent en sens inverse\n")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du calcul de corrélation: {str(e)}")

    def update_statistics(self):
        """Met à jour les statistiques globales"""
        try:
            # Charge les données
            with open('races_database.json', 'r', encoding='utf-8') as f:
                database = json.load(f)
                
            # Filtre les courses selon les critères
            filtered_races = self.filter_races(database['races'])
            
            if not filtered_races:
                messagebox.showinfo("Info", "Aucune course ne correspond aux critères")
                return
                
            # Calcule les statistiques
            total_races = len(filtered_races)
            total_partants = sum(len(race['partants']) for race in filtered_races)
            moyenne_partants = total_partants / total_races if total_races > 0 else 0
            
            # Compte les favoris gagnants
            favoris_gagnants = 0
            courses_valides = 0  # Pour ne compter que les courses avec des cotes valides
            
            for race in filtered_races:
                if not race['infos_course'].get('arrivee'):
                    continue
                    
                try:
                    # Trouve le favori (cote la plus basse) en ignorant les 'NC'
                    cotes_valides = [(float(str(p.get('pmu', '999')).replace(',', '.')), p) 
                                   for p in race['partants'] 
                                   if p.get('pmu') not in ['NC', '', None]]
                    
                    if not cotes_valides:
                        continue
                        
                    favori = min(cotes_valides, key=lambda x: x[0])[1]
                    courses_valides += 1
                    
                    if str(favori['numero']) == race['infos_course']['arrivee'][0]:
                        favoris_gagnants += 1
                        
                except (ValueError, KeyError):
                    continue
                        
            # Calcul des pourcentages en ne considérant que les courses valides
            taux_favoris = (favoris_gagnants / courses_valides * 100) if courses_valides > 0 else 0
            
            # Met à jour les labels
            self.stats_labels['nombre_courses'].config(text=str(total_races))
            self.stats_labels['moyenne_partants'].config(text=f"{moyenne_partants:.1f}")
            self.stats_labels['taux_favoris'].config(text=f"{taux_favoris:.1f}%")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour des statistiques: {str(e)}")

    def filter_races(self, races):
        """Filtre les courses selon les critères sélectionnés"""
        filtered = []
        
        for race in races.values():
            # Filtre par type de course
            if self.race_type.get() != 'Tous':
                if race['infos_course'].get('type_course') != self.race_type.get():
                    continue
                    
            # Filtre par distance
            try:
                distance = int(''.join(filter(str.isdigit, race['infos_course'].get('distance', '0'))))
                if self.distance_min.get() and distance < int(self.distance_min.get()):
                    continue
                if self.distance_max.get() and distance > int(self.distance_max.get()):
                    continue
            except ValueError:
                continue
                
            # Filtre par hippodrome
            if self.track.get():
                if race['infos_course'].get('hippodrome') != self.track.get():
                    continue
                    
            # Filtre par date
            # À implémenter si nécessaire
            
            filtered.append(race)
            
        return filtered
