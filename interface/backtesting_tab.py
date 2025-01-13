import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
from datetime import datetime, timedelta
import json
import os
import sys
from pathlib import Path
import importlib
import inspect
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from core.backtesting_engine import BacktestingEngine, BacktestingConfig, run_backtest
from core.scraper import RaceListScraper, RaceDatabase, RaceScraper
from algos.base_algo import AlgoBase

class FilterSet(ttk.Frame):
    """Widget pour un ensemble de filtres"""
    def __init__(self, parent, on_delete=None):
        super().__init__(parent)
        self.on_delete = on_delete
        
        # En-tête avec titre et bouton de suppression
        header = ttk.Frame(self)
        header.pack(fill='x', pady=(0, 5))
        
        ttk.Label(header, text="Ensemble de filtres").pack(side='left')
        ttk.Button(header, text="×", width=3, command=self._on_delete).pack(side='right')
        
        # Conteneur pour les filtres
        filters = ttk.Frame(self)
        filters.pack(fill='x', padx=5)
        
        # Type de cotes
        row1 = ttk.Frame(filters)
        row1.pack(fill='x', pady=2)
        ttk.Label(row1, text="Type de cotes:").pack(side='left')
        self.odds_type = ttk.Combobox(row1, values=['pmu', 'pmu_fr', 'zeturf'], state='readonly', width=15)
        self.odds_type.set('pmu')
        self.odds_type.pack(side='left', padx=5)
        
        # Type de course
        row2 = ttk.Frame(filters)
        row2.pack(fill='x', pady=2)
        ttk.Label(row2, text="Type de course:").pack(side='left')
        self.type_course = ttk.Combobox(row2, values=['', 'Attelé', 'Monté', 'Plat', 'Haies', 'Steeple-chase'], width=15)
        self.type_course.pack(side='left', padx=5)
        
        # Distance
        row3 = ttk.Frame(filters)
        row3.pack(fill='x', pady=2)
        ttk.Label(row3, text="Distance (m):").pack(side='left')
        self.distance_min = ttk.Entry(row3, width=8)
        self.distance_min.pack(side='left', padx=5)
        ttk.Label(row3, text="à").pack(side='left')
        self.distance_max = ttk.Entry(row3, width=8)
        self.distance_max.pack(side='left', padx=5)
        
        # Allocation
        row4 = ttk.Frame(filters)
        row4.pack(fill='x', pady=2)
        ttk.Label(row4, text="Allocation (€):").pack(side='left')
        self.allocation_min = ttk.Entry(row4, width=8)
        self.allocation_min.pack(side='left', padx=5)
        ttk.Label(row4, text="à").pack(side='left')
        self.allocation_max = ttk.Entry(row4, width=8)
        self.allocation_max.pack(side='left', padx=5)
        
        # Piste
        row5 = ttk.Frame(filters)
        row5.pack(fill='x', pady=2)
        ttk.Label(row5, text="Piste:").pack(side='left')
        self.piste = ttk.Combobox(row5, values=['', 'Piste en herbe', 'Piste en sable', 'Piste en machefer'], width=15)
        self.piste.pack(side='left', padx=5)
        
        # Corde
        row6 = ttk.Frame(filters)
        row6.pack(fill='x', pady=2)
        ttk.Label(row6, text="Corde:").pack(side='left')
        self.corde = ttk.Combobox(row6, values=['', 'Corde à droite', 'Corde à gauche'], width=15)
        self.corde.pack(side='left', padx=5)
        
        # Location
        row7 = ttk.Frame(filters)
        row7.pack(fill='x', pady=2)
        ttk.Label(row7, text="Location:").pack(side='left')
        self.location = ttk.Combobox(row7, values=['', 'Vincennes', 'Saint-Cloud', 'Auteuil', 'Enghien', 'Cagnes-sur-Mer'], width=15)
        self.location.pack(side='left', padx=5)
        
        # Nombre de partants
        row8 = ttk.Frame(filters)
        row8.pack(fill='x', pady=2)
        ttk.Label(row8, text="Nb partants:").pack(side='left')
        self.nb_partants_min = ttk.Entry(row8, width=8)
        self.nb_partants_min.pack(side='left', padx=5)
        ttk.Label(row8, text="à").pack(side='left')
        self.nb_partants_max = ttk.Entry(row8, width=8)
        self.nb_partants_max.pack(side='left', padx=5)
        
        ttk.Separator(self, orient='horizontal').pack(fill='x', pady=10)
        
    def _on_delete(self):
        if self.on_delete:
            self.on_delete(self)
            
    def get_config(self) -> BacktestingConfig:
        """Retourne la configuration des filtres"""
        config = BacktestingConfig()
        
        config.odds_type = self.odds_type.get()
        
        if self.type_course.get():
            config.type_course = [self.type_course.get()]
            
        try:
            if self.distance_min.get():
                config.distance_min = int(self.distance_min.get())
            if self.distance_max.get():
                config.distance_max = int(self.distance_max.get())
        except ValueError:
            pass
            
        try:
            if self.allocation_min.get():
                config.allocation_min = float(self.allocation_min.get())
            if self.allocation_max.get():
                config.allocation_max = float(self.allocation_max.get())
        except ValueError:
            pass
            
        if self.piste.get():
            config.piste = [self.piste.get()]
            
        if self.corde.get():
            config.corde = [self.corde.get()]
            
        if self.location.get():
            config.location = [self.location.get()]
            
        try:
            if self.nb_partants_min.get():
                config.nb_partants_min = int(self.nb_partants_min.get())
            if self.nb_partants_max.get():
                config.nb_partants_max = int(self.nb_partants_max.get())
        except ValueError:
            pass
            
        return config

class BacktestingTab(ttk.Frame):
    """Onglet principal de backtesting"""
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.init_backtesting_interface()
        
    def init_backtesting_interface(self):
        """Initialise l'interface de backtesting"""
        # Chargement des données
        self.load_data()
            
        # Interface principale
        main_frame = ttk.Frame(self, padding="5")
        main_frame.pack(fill='both', expand=True)
            
        # Panneau gauche (filtres)
        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side='left', fill='both', expand=True, padx=5)
        
        filters_frame = ttk.LabelFrame(left_panel, text="Filtres", padding="5")
        filters_frame.pack(fill='x', expand=False)
        
        self.filters_container = ttk.Frame(filters_frame)
        self.filters_container.pack(fill='x', expand=False)
        
        self.filter_sets = []
        self.add_filter_set()
        
        ttk.Button(filters_frame, text="+ Ajouter un filtre", command=self.add_filter_set).pack(pady=5)
        
        # Panneau droit (algorithmes et résultats)
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side='right', fill='both', expand=True, padx=5)
        
        # Section algorithmes
        self.algos_frame = ttk.LabelFrame(right_panel, text="Algorithmes", padding="5")
        self.algos_frame.pack(fill='x', expand=False)
        
        # Maintenant on peut charger les algorithmes
        self.load_algo()
        
        # Section options d'analyse
        analysis_frame = ttk.LabelFrame(right_panel, text="Options d'analyse", padding="5")
        analysis_frame.pack(fill='x', expand=False, pady=5)
        
        # Types de paris disponibles
        betting_frame = ttk.LabelFrame(analysis_frame, text="Types de paris")
        betting_frame.pack(fill='x', padx=5, pady=5)
        
        self.betting_vars = {}
        betting_types = [
            "Simple",
            "Couplé",
            "2 sur 4",
            "Trio",
            "Tiercé",
            "Quarté",
            "Quinté",
            "Multi"
        ]
        
        # Ajoute une case à cocher pour chaque type de pari
        for i, bet_type in enumerate(betting_types):
            var = tk.BooleanVar(value=True if bet_type in ["Simple", "Couplé"] else False)
            self.betting_vars[bet_type] = var
            ttk.Checkbutton(
                betting_frame,
                text=bet_type,
                variable=var
            ).grid(row=i//3, column=i%3, sticky='w', padx=5, pady=2)
        
        # Opérateur
        operator_frame = ttk.Frame(analysis_frame)
        operator_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(operator_frame, text="Opérateur:").pack(side='left')
        self.operator_var = ttk.Combobox(
            operator_frame,
            values=["PMU", "PMU.fr", "ZEturf"],
            state='readonly',
            width=10
        )
        self.operator_var.set("PMU")
        self.operator_var.pack(side='left', padx=5)
        
        ttk.Button(right_panel, text="Lancer le backtesting", 
                   command=self.run_backtest).pack(pady=5)
        
        # Section résultats
        results_frame = ttk.LabelFrame(right_panel, text="Résultats", padding="5")
        results_frame.pack(fill='both', expand=True, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(results_frame, height=20)
        self.results_text.pack(fill='both', expand=True)

    def load_data(self):
        """Charge les données des courses"""
        try:
            with open('races_database.json', 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {'races': {}}

    def load_algo(self):
        """Charge dynamiquement tous les algorithmes depuis le dossier algos"""
        self.algos = []
        algos = []
        
        try:
            # Obtient le chemin du dossier algos
            root_dir = Path(__file__).parent.parent
            algos_dir = root_dir / 'algos'
            
            if not algos_dir.exists():
                print(f"Dossier algos non trouvé: {algos_dir}")
                return
            
            # Liste tous les fichiers Python dans le dossier algos
            algo_files = [f for f in algos_dir.glob('*.py') 
                         if f.name != 'base_algo.py' and f.name != '__init__.py']
            
            # Pour chaque fichier, importe les classes qui héritent de AlgoBase
            for file_path in algo_files:
                module_name = file_path.stem
                try:
                    # Import dynamique du module
                    spec = importlib.util.spec_from_file_location(
                        module_name, str(file_path))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Trouve toutes les classes dans le module qui héritent de AlgoBase
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, AlgoBase) and 
                            obj != AlgoBase):  # Exclut la classe de base
                            try:
                                # Instancie l'algorithme pour vérifier qu'il fonctionne
                                algo = obj()
                                algos.append(algo)
                            except Exception as e:
                                print(f"Erreur lors de l'instanciation de {name}: {e}")
                                
                except ImportError as e:
                    print(f"Erreur lors de l'import de {module_name}: {e}")
            
            # Trie les algorithmes par nom pour un affichage cohérent
            algos.sort(key=lambda x: x.name)
            
            # Construction des RadioButtons avec le nom réel de l'algorithme
            self.algo_var = tk.StringVar()
            for algo in algos:
                ttk.Radiobutton(
                    self.algos_frame,
                    text=algo.name,
                    variable=self.algo_var,
                    value=algo.__class__.__name__
                ).pack(anchor='w')
                
                # Stocke la classe d'algorithme (pas l'instance)
                self.algos.append(algo.__class__)
                
            if self.algos:
                self.algo_var.set(self.algos[0].__name__)
                
        except Exception as e:
            print(f"Erreur lors du chargement des algorithmes: {e}")
            self.algos = []
            
    def add_filter_set(self):
        """Ajoute un nouvel ensemble de filtres"""
        filter_set = FilterSet(self.filters_container, self.remove_filter_set)
        filter_set.pack(fill='x', expand=False)
        self.filter_sets.append(filter_set)
        
    def remove_filter_set(self, filter_set):
        """Supprime un ensemble de filtres"""
        filter_set.pack_forget()
        filter_set.destroy()
        self.filter_sets.remove(filter_set)
        
    def run_backtest(self):
        """Lance le backtesting avec les paramètres sélectionnés"""
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, "Backtesting en cours...\n\n")
        self.update()
        
        try:
            # Récupère l'algorithme sélectionné
            algo_class = next(a for a in self.algos if a.__name__ == self.algo_var.get())
            algo = algo_class()
            
            # Récupère les types de paris sélectionnés
            selected_bets = [
                bet_type for bet_type, var in self.betting_vars.items() 
                if var.get()
            ]
            
            # Récupère les configurations des filtres
            configs = [fs.get_config() for fs in self.filter_sets]
            
            # Ajoute les options de paris à chaque configuration
            for config in configs:
                config.operateur = self.operator_var.get()
                config.paris_selectionnes = selected_bets
            
            # Lance le backtesting pour chaque configuration
            all_results = []
            for config in configs:
                results = run_backtest(self.data['races'], algo, config)
                all_results.append(results)
                
            # Affiche les résultats
            self.display_results(all_results, configs)
            
        except Exception as e:
            self.results_text.insert(tk.END, f"Erreur lors du backtesting: {str(e)}\n")
            
    def display_results(self, all_results, filter_configs):
        """Affiche les résultats du backtesting"""
        self.results_text.delete('1.0', tk.END)

        # Calcul des totaux globaux
        total_races = sum(r.total_races for r in all_results)
        if total_races == 0:
            self.results_text.insert(tk.END, "Aucune course trouvée avec ces critères.\n")
            return

        # Affichage des résultats globaux
        self.results_text.insert(tk.END, "=== RÉSULTATS GLOBAUX ===\n\n")
        self.results_text.insert(tk.END, f"Nombre total de courses analysées: {total_races}\n\n")

        # Résultats financiers globaux
        total_bets = sum(r.total_bets for r in all_results)
        total_returns = sum(r.total_returns for r in all_results)
        global_roi = ((total_returns - total_bets) / total_bets * 100) if total_bets > 0 else 0

        self.results_text.insert(tk.END, f"\n=== RÉSULTATS FINANCIERS ===\n")
        self.results_text.insert(tk.END, f"Total misé: {total_bets:.2f}€\n")
        self.results_text.insert(tk.END, f"Total gains: {total_returns:.2f}€\n")
        self.results_text.insert(tk.END, f"ROI: {global_roi:.2f}%\n")

        # Résultats détaillés par filtre
        self.results_text.insert(tk.END, "\n=== DÉTAIL PAR FILTRE ===\n")
        for i, (results, config) in enumerate(zip(all_results, filter_configs), 1):
            self.results_text.insert(tk.END, f"\nFiltre {i}:\n")
            summary = results.get_summary()

            self.results_text.insert(tk.END, f"Courses: {summary['total_races']}\n")
            self.results_text.insert(tk.END, f"ROI: {summary['roi']}%\n")

            # Détails des critères du filtre
            self.results_text.insert(tk.END, "Critères appliqués:\n")
            for key, value in vars(config).items():
                if value:  # N'affiche que les critères non vides
                    self.results_text.insert(tk.END, f"  {key}: {value}\n")

    def export_results(self):
        """Exporte les résultats en CSV"""
        try:
            if not hasattr(self, 'current_results'):
                messagebox.showwarning("Export", "Aucun résultat à exporter")
                return
                
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=f"backtest_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )
            
            if not filename:
                return
                
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Course', 'Date', 'Prédiction', 'Résultat', 'ROI'])
                
                for result in self.current_results:
                    writer.writerow([
                        result['course'],
                        result['date'],
                        ','.join(map(str, result['prediction'])),
                        ','.join(map(str, result['resultat'])),
                        f"{result['roi']:.2f}%"
                    ])
                    
            messagebox.showinfo("Export réussi", "Les résultats ont été exportés avec succès.")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'export: {str(e)}")

    def show_charts(self):
        """Affiche les graphiques de performance"""
        if not hasattr(self, 'current_results'):
            messagebox.showwarning("Graphiques", "Aucun résultat à afficher")
            return
            
        # Crée une nouvelle fenêtre
        chart_window = tk.Toplevel(self)
        chart_window.title("Graphiques de Performance")
        chart_window.geometry("800x600")
        
        # Notebook pour différents graphiques
        nb = ttk.Notebook(chart_window)
        nb.pack(fill='both', expand=True)
        
        # ROI cumulé
        roi_frame = ttk.Frame(nb)
        nb.add(roi_frame, text='ROI Cumulé')
        
        fig1 = Figure(figsize=(8, 5))
        ax1 = fig1.add_subplot(111)
        
        # Calcul du ROI cumulé
        cumulative_roi = []
        roi_sum = 0
        for result in self.current_results:
            roi_sum += result['roi']
            cumulative_roi.append(roi_sum)
            
        ax1.plot(cumulative_roi)
        ax1.set_title('ROI Cumulé')
        ax1.set_xlabel('Courses')
        ax1.set_ylabel('ROI (%)')
        ax1.grid(True)
        
        canvas1 = FigureCanvasTkAgg(fig1, roi_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(fill='both', expand=True)
