import os
import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk

# Ajout du chemin racine au PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.absolute()
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
print(f"Chemin racine ajouté : {ROOT_DIR}")
print(f"Démarrage de l'application depuis : {__file__}")

# Imports des onglets
from interface.analysis_tab import AnalysisTab
from interface.algo_creation_tab import AlgoCreationTab
from interface.strategy_creation_tab import StrategyCreationTab
from interface.backtesting_tab import BacktestingTab
from interface.scraping_tab import ScrapingTab

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("PegaZeus - Analyse de Courses")
        
        # Configuration de la fenêtre
        self.setup_window()
        
        # Création du notebook principal
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Création des onglets
        self.create_tabs()
        
        # Menu
        self.create_menu()

    def setup_window(self):
        """Configure la fenêtre principale"""
        # Taille par défaut 80% de l'écran
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = int(screen_width * 0.8)
        height = int(screen_height * 0.8)
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Active le redimensionnement
        self.root.resizable(True, True)

    def create_tabs(self):
        """Crée tous les onglets de l'application"""
        try:
            # Onglet Analyse
            self.analysis_tab = AnalysisTab(self.notebook)
            self.notebook.add(self.analysis_tab, text='Analyse')
            
            # Onglet Création Algo
            self.algo_creation_tab = AlgoCreationTab(self.notebook)
            self.notebook.add(self.algo_creation_tab, text='Création Algo')
            
            # Onglet Création Stratégie
            self.strategy_creation_tab = StrategyCreationTab(self.notebook)
            self.notebook.add(self.strategy_creation_tab, text='Création Stratégie')
            
            # Onglet Backtesting
            self.backtesting_tab = BacktestingTab(self.notebook)
            self.notebook.add(self.backtesting_tab, text='Backtesting')
            
            # Onglet Scraping
            self.scraping_tab = ScrapingTab(self.notebook)
            self.notebook.add(self.scraping_tab, text='Scraping')
            
        except Exception as e:
            print(f"Erreur lors de la création des onglets: {e}")
            import traceback
            traceback.print_exc()

    def create_menu(self):
        """Crée le menu de l'application"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouvelle analyse", command=self.new_analysis)
        file_menu.add_command(label="Ouvrir", command=self.open_file)
        file_menu.add_command(label="Sauvegarder", command=self.save_file)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.root.quit)
        
        # Menu Edition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edition", menu=edit_menu)
        edit_menu.add_command(label="Préférences", command=self.show_preferences)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="À propos", command=self.show_about)

    # Méthodes pour les actions du menu
    def new_analysis(self):
        """Crée une nouvelle analyse"""
        pass

    def open_file(self):
        """Ouvre un fichier"""
        pass

    def save_file(self):
        """Sauvegarde le fichier courant"""
        pass

    def show_preferences(self):
        """Affiche la fenêtre des préférences"""
        pass

    def show_documentation(self):
        """Affiche la documentation"""
        pass

    def show_about(self):
        """Affiche la fenêtre À propos"""
        pass

def main():
    root = tk.Tk()
    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
