import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os
from pathlib import Path

class StrategyCreationTab(ttk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.current_strategy = None
        self.setup_ui()
        self.bind_events()

    def setup_ui(self):
        """Initialise l'interface utilisateur"""
        self.pack(fill='both', expand=True)

        # Configuration des colonnes principales
        self.columnconfigure(0, weight=1)  # Panneau gauche
        self.columnconfigure(1, weight=2)  # Panneau central
        self.columnconfigure(2, weight=1)  # Panneau droit

        self.setup_left_panel()
        self.setup_center_panel()
        self.setup_right_panel()

    def setup_left_panel(self):
        """Configuration du panneau gauche (algorithmes disponibles)"""
        left_panel = ttk.LabelFrame(self, text="Algorithmes disponibles")
        left_panel.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)

        # Liste des algorithmes
        self.algo_list = ttk.Treeview(left_panel, 
                                    columns=('Nom', 'Performance'),
                                    show='headings',
                                    selectmode='extended')
        self.algo_list.heading('Nom', text='Nom')
        self.algo_list.heading('Performance', text='Performance')
        self.algo_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Boutons d'action
        btn_frame = ttk.Frame(left_panel)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Ajouter →", command=self.add_algorithm).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="← Retirer", command=self.remove_algorithm).pack(side='left', padx=2)

    def setup_center_panel(self):
        """Configuration du panneau central (paramètres de stratégie)"""
        center_panel = ttk.Frame(self)
        center_panel.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)

        # Informations de base
        info_frame = ttk.LabelFrame(center_panel, text="Informations")
        info_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(info_frame, text="Nom de la stratégie:").pack(anchor='w', padx=5, pady=2)
        self.strategy_name = ttk.Entry(info_frame)
        self.strategy_name.pack(fill='x', padx=5, pady=2)

        ttk.Label(info_frame, text="Description:").pack(anchor='w', padx=5, pady=2)
        self.strategy_desc = tk.Text(info_frame, height=3, wrap='word')
        self.strategy_desc.pack(fill='x', padx=5, pady=2)

        # Configuration des règles
        rules_frame = ttk.LabelFrame(center_panel, text="Configuration")
        rules_frame.pack(fill='x', padx=5, pady=5)

        # Type de pari
        ttk.Label(rules_frame, text="Type de pari:").pack(anchor='w', padx=5, pady=2)
        self.bet_type = ttk.Combobox(rules_frame, values=[
            'Simple G/P', 'Couplé G/P', '2sur4', 'Tiercé', 'Quarté', 'Quinté'
        ], state='readonly')
        self.bet_type.pack(fill='x', padx=5, pady=2)

        # Sélection chevaux
        ttk.Label(rules_frame, text="Sélection chevaux:").pack(anchor='w', padx=5, pady=2)
        self.horse_selection = ttk.Combobox(rules_frame, values=[
            'Premier uniquement', 'Deux premiers', 'Trois premiers', 
            'Quatre premiers', 'Les cinq'
        ], state='readonly')
        self.horse_selection.pack(fill='x', padx=5, pady=2)

        # Conditions
        cond_frame = ttk.LabelFrame(rules_frame, text="Conditions")
        cond_frame.pack(fill='x', padx=5, pady=5)

        # Cotes min/max
        odds_frame = ttk.Frame(cond_frame)
        odds_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(odds_frame, text="Cotes:").pack(side='left', padx=5)
        ttk.Label(odds_frame, text="Min:").pack(side='left')
        self.min_odds = ttk.Entry(odds_frame, width=6)
        self.min_odds.pack(side='left', padx=2)
        ttk.Label(odds_frame, text="Max:").pack(side='left', padx=5)
        self.max_odds = ttk.Entry(odds_frame, width=6)
        self.max_odds.pack(side='left', padx=2)

        # Seuil de confiance
        ttk.Label(cond_frame, text="Seuil de confiance:").pack(anchor='w', padx=5, pady=2)
        self.confidence_threshold = ttk.Scale(cond_frame, from_=0, to=100,
                                           orient='horizontal')
        self.confidence_threshold.pack(fill='x', padx=5, pady=2)

        # Filtres spécifiques
        filters_frame = ttk.LabelFrame(center_panel, text="Filtres")
        filters_frame.pack(fill='x', padx=5, pady=5)

        # Type de course
        ttk.Label(filters_frame, text="Type de course:").pack(anchor='w', padx=5, pady=2)
        self.race_type = ttk.Combobox(filters_frame, values=[
            'Tout', 'Plat', 'Obstacle', 'Trot'
        ], state='readonly')
        self.race_type.pack(fill='x', padx=5, pady=2)

        # Distance
        distance_frame = ttk.Frame(filters_frame)
        distance_frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(distance_frame, text="Distance (m):").pack(side='left')
        self.min_distance = ttk.Entry(distance_frame, width=6)
        self.min_distance.pack(side='left', padx=2)
        ttk.Label(distance_frame, text="à").pack(side='left', padx=2)
        self.max_distance = ttk.Entry(distance_frame, width=6)
        self.max_distance.pack(side='left', padx=2)

    def setup_right_panel(self):
        """Configuration du panneau droit (stratégies actives)"""
        right_panel = ttk.LabelFrame(self, text="Stratégies actives")
        right_panel.grid(row=0, column=2, sticky='nsew', padx=5, pady=5)

        # Liste des stratégies
        self.strategy_list = ttk.Treeview(right_panel, 
                                        columns=('Nom', 'Type', 'Algos'),
                                        show='headings')
        self.strategy_list.heading('Nom', text='Nom')
        self.strategy_list.heading('Type', text='Type')
        self.strategy_list.heading('Algos', text='Algorithmes')
        self.strategy_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Boutons d'action
        btn_frame = ttk.Frame(right_panel)
        btn_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(btn_frame, text="Nouveau", command=self.new_strategy).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Sauvegarder", command=self.save_strategy).pack(side='left', padx=2)
        ttk.Button(btn_frame, text="Supprimer", command=self.delete_strategy).pack(side='left', padx=2)

    def bind_events(self):
        """Lie les événements aux widgets"""
        self.strategy_list.bind('<<TreeviewSelect>>', self.on_strategy_select)

    def load_algorithms(self):
        """Charge la liste des algorithmes disponibles"""
        try:
            for item in self.algo_list.get_children():
                self.algo_list.delete(item)

            algos_dir = Path(__file__).parent.parent / 'algos'
            if not algos_dir.exists():
                messagebox.showerror("Erreur", "Dossier des algorithmes introuvable")
                return

            for file in algos_dir.glob('*.py'):
                if file.name != 'base_algo.py' and file.name != '__init__.py':
                    algo_name = file.stem
                    self.algo_list.insert('', 'end', values=(algo_name, "N/A"))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des algorithmes: {str(e)}")

    def load_strategies(self):
        """Charge les stratégies existantes"""
        try:
            for item in self.strategy_list.get_children():
                self.strategy_list.delete(item)

            strategies_file = Path(__file__).parent.parent / 'data' / 'strategies.json'
            if not strategies_file.exists():
                return

            with strategies_file.open('r', encoding='utf-8') as f:
                strategies = json.load(f)

            for strategy in strategies:
                self.strategy_list.insert('', 'end', values=(
                    strategy['name'],
                    strategy['bet_type'],
                    ', '.join(strategy.get('algorithms', []))
                ))
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des stratégies: {str(e)}")

    def new_strategy(self):
        """Crée une nouvelle stratégie"""
        self.clear_form()
        self.current_strategy = None

    def clear_form(self):
        """Vide le formulaire"""
        self.strategy_name.delete(0, tk.END)
        self.strategy_desc.delete('1.0', tk.END)
        self.bet_type.set('')
        self.horse_selection.set('')
        self.min_odds.delete(0, tk.END)
        self.max_odds.delete(0, tk.END)
        self.confidence_threshold.set(0)
        self.race_type.set('')
        self.min_distance.delete(0, tk.END)
        self.max_distance.delete(0, tk.END)

    def add_algorithm(self):
        """Ajoute un algorithme à la stratégie courante"""
        selections = self.algo_list.selection()
        if not selections:
            messagebox.showwarning("Attention", "Veuillez sélectionner un algorithme")
            return

        if not self.strategy_name.get().strip():
            messagebox.showwarning("Attention", "Veuillez d'abord nommer la stratégie")
            return

        selected_algos = []
        for item in self.strategy_list.get_children():
            values = self.strategy_list.item(item)['values']
            if values[0] == self.strategy_name.get():
                if values[2]:
                    selected_algos = values[2].split(', ')
                break

        for sel in selections:
            algo_name = self.algo_list.item(sel)['values'][0]
            if algo_name not in selected_algos:
                selected_algos.append(algo_name)

        self.update_strategy_list(selected_algos)

    def remove_algorithm(self):
        """Retire un algorithme de la stratégie courante"""
        strategy_sel = self.strategy_list.selection()
        if not strategy_sel:
            messagebox.showwarning("Attention", "Veuillez sélectionner une stratégie")
            return

        algo_sel = self.algo_list.selection()
        if not algo_sel:
            messagebox.showwarning("Attention", "Veuillez sélectionner un algorithme à retirer")
            return

        values = self.strategy_list.item(strategy_sel[0])['values']
        current_algos = values[2].split(', ') if values[2] else []
        algos_to_remove = [self.algo_list.item(sel)['values'][0] for sel in algo_sel]
        updated_algos = [algo for algo in current_algos if algo not in algos_to_remove]

        self.update_strategy_list(updated_algos)

    def update_strategy_list(self, algorithms):
        """Met à jour la liste des stratégies"""
        strategy_name = self.strategy_name.get()
        bet_type = self.bet_type.get()

        # Mise à jour ou création
        found = False
        for item in self.strategy_list.get_children():
            if self.strategy_list.item(item)['values'][0] == strategy_name:
                self.strategy_list.item(item, values=(
                    strategy_name,
                    bet_type,
                    ', '.join(algorithms)
                ))
                found = True
                break

        if not found:
            self.strategy_list.insert('', 'end', values=(
                strategy_name,
                bet_type,
                ', '.join(algorithms)
            ))

    def on_strategy_select(self, event):
        """Gère la sélection d'une stratégie"""
        selection = self.strategy_list.selection()
        if not selection:
            return

        values = self.strategy_list.item(selection[0])['values']
        self.load_strategy(values[0])

    def load_strategy(self, strategy_name):
        """Charge une stratégie dans le formulaire"""
        try:
            strategies_file = Path(__file__).parent.parent / 'data' / 'strategies.json'
            with strategies_file.open('r', encoding='utf-8') as f:
                strategies = json.load(f)

            strategy = next((s for s in strategies if s['name'] == strategy_name), None)
            if not strategy:
                return

            self.current_strategy = strategy
            self.clear_form()

            # Remplit le formulaire
            self.strategy_name.insert(0, strategy['name'])
            self.strategy_desc.insert('1.0', strategy.get('description', ''))
            self.bet_type.set(strategy['bet_type'])
            self.horse_selection.set(strategy.get('horse_selection', ''))
            
            conditions = strategy.get('conditions', {})
            if 'min_odds' in conditions:
                self.min_odds.insert(0, str(conditions['min_odds']))
            if 'max_odds' in conditions:
                self.max_odds.insert(0, str(conditions['max_odds']))
            if 'confidence_threshold' in conditions:
                self.confidence_threshold.set(conditions['confidence_threshold'])

            filters = strategy.get('filters', {})
            self.race_type.set(filters.get('race_type', ''))
            if 'min_distance' in filters:
                self.min_distance.insert(0, str(filters['min_distance']))
            if 'max_distance' in filters:
                self.max_distance.insert(0, str(filters['max_distance']))

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement de la stratégie: {str(e)}")

    def validate_strategy(self) -> bool:
        """Valide les données de la stratégie"""
        if not self.strategy_name.get().strip():
            messagebox.showwarning("Validation", "Le nom de la stratégie est requis")
            return False

        if not self.bet_type.get():
            messagebox.showwarning("Validation", "Le type de pari est requis")
            return False

        if not self.horse_selection.get():
            messagebox.showwarning("Validation", "La sélection de chevaux est requise")
            return False

        # Validation des cotes
        try:
            if self.min_odds.get():
                min_odds = float(self.min_odds.get())
                if min_odds < 0:
                    messagebox.showwarning("Validation", "La cote minimale doit être positive")
                    return False
            if self.max_odds.get():
                max_odds = float(self.max_odds.get())
                if max_odds < 0:
                    messagebox.showwarning("Validation", "La cote maximale doit être positive")
                    return False
            if self.min_odds.get() and self.max_odds.get():
                if min_odds > max_odds:
                    messagebox.showwarning("Validation", "La cote minimale doit être inférieure à la maximale")
                    return False
        except ValueError:
            messagebox.showwarning("Validation", "Les cotes doivent être des nombres valides")
            return False

        # Validation des distances
        try:
            if self.min_distance.get():
                min_dist = int(self.min_distance.get())
                if min_dist < 0:
                    messagebox.showwarning("Validation", "La distance minimale doit être positive")
                    return False
            if self.max_distance.get():
                max_dist = int(self.max_distance.get())
                if max_dist < 0:
                    messagebox.showwarning("Validation", "La distance maximale doit être positive")
                    return False
            if self.min_distance.get() and self.max_distance.get():
                if min_dist > max_dist:
                    messagebox.showwarning("Validation", "La distance minimale doit être inférieure à la maximale")
                    return False
        except ValueError:
            messagebox.showwarning("Validation", "Les distances doivent être des nombres entiers")
            return False

        return True

    def save_strategy(self):
        """Sauvegarde la stratégie"""
        try:
            if not self.validate_strategy():
                return

            strategy = {
                'name': self.strategy_name.get().strip(),
                'description': self.strategy_desc.get('1.0', tk.END).strip(),
                'bet_type': self.bet_type.get(),
                'horse_selection': self.horse_selection.get(),
                'conditions': {
                    'min_odds': float(self.min_odds.get()) if self.min_odds.get() else None,
                    'max_odds': float(self.max_odds.get()) if self.max_odds.get() else None,
                    'confidence_threshold': self.confidence_threshold.get()
                },
                'filters': {
                    'race_type': self.race_type.get(),
                    'min_distance': int(self.min_distance.get()) if self.min_distance.get() else None,
                    'max_distance': int(self.max_distance.get()) if self.max_distance.get() else None
                }
            }

            # Récupère les algorithmes associés
            for item in self.strategy_list.get_children():
                if self.strategy_list.item(item)['values'][0] == strategy['name']:
                    algos_str = self.strategy_list.item(item)['values'][2]
                    strategy['algorithms'] = algos_str.split(', ') if algos_str else []
                    break

            # Assure que le dossier data existe
            data_dir = Path(__file__).parent.parent / 'data'
            data_dir.mkdir(exist_ok=True)

            strategies_file = data_dir / 'strategies.json'
            strategies = []
            if strategies_file.exists():
                with strategies_file.open('r', encoding='utf-8') as f:
                    strategies = json.load(f)

            # Met à jour ou ajoute la stratégie
            strategy_index = next((i for i, s in enumerate(strategies) 
                                if s['name'] == strategy['name']), None)
            if strategy_index is not None:
                strategies[strategy_index] = strategy
            else:
                strategies.append(strategy)

            # Sauvegarde le fichier
            with strategies_file.open('w', encoding='utf-8') as f:
                json.dump(strategies, f, indent=4, ensure_ascii=False)

            messagebox.showinfo("Succès", "Stratégie sauvegardée avec succès!")
            self.load_strategies()  # Rafraîchit la liste

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la sauvegarde: {str(e)}")

    def delete_strategy(self):
        """Supprime la stratégie sélectionnée"""
        selection = self.strategy_list.selection()
        if not selection:
            messagebox.showwarning("Attention", "Veuillez sélectionner une stratégie à supprimer")
            return

        if not messagebox.askyesno("Confirmation", 
                                 "Êtes-vous sûr de vouloir supprimer cette stratégie ?"):
            return

        try:
            strategy_name = self.strategy_list.item(selection[0])['values'][0]
            strategies_file = Path(__file__).parent.parent / 'data' / 'strategies.json'

            if strategies_file.exists():
                with strategies_file.open('r', encoding='utf-8') as f:
                    strategies = json.load(f)

                strategies = [s for s in strategies if s['name'] != strategy_name]

                with strategies_file.open('w', encoding='utf-8') as f:
                    json.dump(strategies, f, indent=4, ensure_ascii=False)

            self.strategy_list.delete(selection[0])
            self.clear_form()
            messagebox.showinfo("Succès", "Stratégie supprimée avec succès!")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la suppression: {str(e)}")
