import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from core.scraper import RaceListScraper, RaceDatabase, RaceScraper

class ScrapingTab(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setup_ui()
        self.scraping_in_progress = False
        
    def setup_ui(self):
        """Initialise l'interface utilisateur"""
        # Frame principal avec padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill='both', expand=True)
        
        # === Section Courses Récentes ===
        recent_frame = ttk.LabelFrame(main_frame, text="Scraping des courses récentes", padding="5")
        recent_frame.pack(fill='x', pady=(0, 10))
        
        # Options de scraping
        options_frame = ttk.Frame(recent_frame)
        options_frame.pack(fill='x', pady=5)
        
        self.scraping_vars = {}
        options = [
            ("Informations course", "race_info"),
            ("Partants", "runners"),
            ("Cotes", "odds"),
            ("Types de paris", "betting_types"),
            ("Gains potentiels", "potential_gains"),
            ("Historique performances", "performance_history"),
            ("Météo", "weather_info"),
            ("Coefficients", "coefficients"),
            ("Musique", "musique"),
            ("Connexions", "connections"),
            ("Oeillères/Ferrures", "equipment"),
            ("Indicateurs jour/réunion", "daily_indicators"),
            ("Statistiques jockey", "jockey_stats"),
            ("Statistiques entraîneur", "trainer_stats"),
            ("Statistiques cheval", "horse_stats"),
            ("Profil piste", "track_profile"),
            ("Gains", "earnings"),
            ("Appétences", "preferences")
        ]
        
        for i, (option_text, option_key) in enumerate(options):
            var = tk.BooleanVar(value=True)
            self.scraping_vars[option_key] = var
            ttk.Checkbutton(
                options_frame, 
                text=option_text,
                variable=var
            ).grid(row=i//3, column=i%3, sticky='w', padx=5, pady=2)
        
        # Contrôles pour le nombre de courses
        controls_frame = ttk.Frame(recent_frame)
        controls_frame.pack(fill='x', pady=5)
        
        self.max_races_var = tk.StringVar(value="all")
        ttk.Radiobutton(
            controls_frame,
            text="Toutes les courses",
            variable=self.max_races_var,
            value="all"
        ).pack(side='left', padx=5)
        
        ttk.Radiobutton(
            controls_frame,
            text="Limiter à:",
            variable=self.max_races_var,
            value="limited"
        ).pack(side='left', padx=5)
        
        self.max_races_entry = ttk.Entry(controls_frame, width=5)
        self.max_races_entry.pack(side='left', padx=2)
        ttk.Label(controls_frame, text="courses").pack(side='left', padx=2)
        
        # === Section URL Spécifique ===
        url_frame = ttk.LabelFrame(main_frame, text="Scraping par URL", padding="5")
        url_frame.pack(fill='x', pady=10)
        
        # Champ URL
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill='x', pady=5)
        
        ttk.Label(url_input_frame, text="URL:").pack(side='left', padx=5)
        self.url_entry = ttk.Entry(url_input_frame)
        self.url_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Boutons d'action
        button_frame = ttk.Frame(url_frame)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            button_frame,
            text="Scraper cette URL",
            command=self.start_url_scraping
        ).pack(side='left', padx=5)
        
        ttk.Button(
            button_frame,
            text="Scraper courses récentes",
            command=self.start_recent_scraping
        ).pack(side='left', padx=5)
        
        # === Section Dates ===
        date_frame = ttk.LabelFrame(main_frame, text="Scraping par dates", padding="5")
        date_frame.pack(fill='x', pady=10)
        
        date_input_frame = ttk.Frame(date_frame)
        date_input_frame.pack(fill='x', pady=5)
        
        ttk.Label(date_input_frame, text="Du:").pack(side='left', padx=5)
        self.start_date_entry = ttk.Entry(date_input_frame, width=10)
        self.start_date_entry.pack(side='left', padx=5)
        ttk.Label(date_input_frame, text="(AAAA-MM-JJ)").pack(side='left', padx=2)
        
        ttk.Label(date_input_frame, text="Au:").pack(side='left', padx=5)
        self.end_date_entry = ttk.Entry(date_input_frame, width=10)
        self.end_date_entry.pack(side='left', padx=5)
        ttk.Label(date_input_frame, text="(AAAA-MM-JJ)").pack(side='left', padx=2)
        
        ttk.Button(date_frame, text="Scraper cette période", 
                  command=self.start_date_range_scraping).pack(pady=5)
        
        # === Zone de Logs ===
        log_frame = ttk.LabelFrame(main_frame, text="Logs", padding="5")
        log_frame.pack(fill='both', expand=True, pady=10)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10)
        self.log_text.pack(fill='both', expand=True)
        
        # === Barre de progression ===
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, 
                                      variable=self.progress_var,
                                      maximum=100)
        self.progress.pack(fill='x', pady=5)

    def get_scraping_config(self):
        """Retourne la configuration de scraping"""
        config = {
            "scraping_options": {
                name: var.get() for name, var in self.scraping_vars.items()
            },
            "delay_between_requests": 2,
            "headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }
        
        if self.max_races_var.get() == "limited":
            try:
                config["max_races"] = int(self.max_races_entry.get())
            except ValueError:
                config["max_races"] = -1
        else:
            config["max_races"] = -1
            
        return config
        
    def start_recent_scraping(self):
        """Lance le scraping des courses récentes"""
        if self.scraping_in_progress:
            messagebox.showwarning("En cours", 
                                 "Un scraping est déjà en cours.")
            return
            
        def scraping_thread():
            self.scraping_in_progress = True
            try:
                config = self.get_scraping_config()
                scraper = RaceListScraper(config)
                scraper.log_callback = lambda message: self.after(0, self.log, message)
                scraper.progress_callback = lambda value: self.after(0, self.update_progress, value)
                scraper.scrape_races()
                
            except Exception as e:
                self.after(0, messagebox.showerror, "Erreur", str(e))
            finally:
                self.scraping_in_progress = False
                self.after(0, self.update_progress, 0)
                
        thread = threading.Thread(target=scraping_thread)
        thread.daemon = True
        thread.start()

    def start_url_scraping(self):
        """Lance le scraping d'une URL spécifique"""
        if self.scraping_in_progress:
            messagebox.showwarning("En cours", 
                                 "Un scraping est déjà en cours.")
            return
            
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("URL manquante", 
                                 "Veuillez entrer une URL.")
            return
        
        def scraping_thread():
            self.scraping_in_progress = True
            try:
                config = self.get_scraping_config()
                config['url'] = url
                
                scraper = RaceScraper(url, config['scraping_options'])
                self.log(f"Début du scraping : {url}")
                race_data = scraper.scrape()
                
                db = RaceDatabase()
                db.add_race(race_data)
                db.save()
                
                self.log("Scraping terminé avec succès")
                
            except Exception as e:
                self.after(0, messagebox.showerror, "Erreur", str(e))
            finally:
                self.scraping_in_progress = False
                self.after(0, self.update_progress, 0)
                
        thread = threading.Thread(target=scraping_thread)
        thread.daemon = True
        thread.start()

    def start_date_range_scraping(self):
        """Lance le scraping pour une plage de dates"""
        if self.scraping_in_progress:
            messagebox.showwarning("En cours", 
                                 "Un scraping est déjà en cours.")
            return
            
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        
        if not start_date or not end_date:
            messagebox.showwarning("Dates manquantes",
                                 "Veuillez entrer une date de début et une date de fin.")
            return
            
        if not self.validate_date(start_date) or not self.validate_date(end_date):
            messagebox.showwarning("Format incorrect",
                                 "Les dates doivent être au format AAAA-MM-JJ")
            return
        
        def scraping_thread():
            self.scraping_in_progress = True
            try:
                dates = self.get_dates_range(start_date, end_date)
                total_new_races = 0
                
                for i, date in enumerate(dates):
                    url = f"https://www.site-courses.fr/archive/{date}"
                    config = self.get_scraping_config()
                    config['url'] = url
                    
                    scraper = RaceListScraper(config)
                    scraper.log_callback = lambda message: self.after(0, self.log, message)
                    scraper.scrape_races()
                    
                    # Met à jour la progression
                    progress = ((i + 1) / len(dates)) * 100
                    self.after(0, self.update_progress, progress)
                    
                    self.log(f"Scraping terminé pour la date {date}")
                    
            except Exception as e:
                self.after(0, messagebox.showerror, "Erreur", str(e))
            finally:
                self.scraping_in_progress = False
                self.after(0, self.update_progress, 0)
                
        thread = threading.Thread(target=scraping_thread)
        thread.daemon = True
        thread.start()

    def validate_date(self, date_str):
        """Valide le format de la date"""
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def get_dates_range(self, start_date, end_date):
        """Génère la liste des dates entre start_date et end_date"""
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        date_list = []
        current = start
        while current <= end:
            date_list.append(current.strftime('%Y-%m-%d'))
            current += timedelta(days=1)
            
        return date_list

    def log(self, message):
        """Ajoute un message aux logs"""
        self.log_text.insert('end', f"{message}\n")
        self.log_text.see('end')

    def update_progress(self, value):
        """Met à jour la barre de progression"""
        self.progress_var.set(value)
