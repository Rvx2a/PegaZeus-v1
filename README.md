# PegaZeus-v1

Outil avancé d'analyse de courses hippiques et de création de stratégies de paris.

## 🎯 Caractéristiques

- **Analyse Statistique** : Visualisation et analyse des données historiques
- **Création d'Algorithmes** : Interface de développement d'algorithmes prédictifs
- **Stratégies de Paris** : Configuration de stratégies basées sur les algorithmes
- **Backtesting** : Tests et validation des stratégies
- **Bot Discord** : Partage automatisé des prédictions
- **Scraping** : Gestion de la collecte de données

## 🚀 Installation

1. Cloner le repository
```bash
git clone https://github.com/Rvx2a/PegaZeus-v1.git
cd PegaZeus-v1
```

2. Créer un environnement virtuel
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## 🔧 Configuration

1. Copier le fichier `.env.example` vers `.env`
2. Configurer les variables d'environnement nécessaires
3. Configurer les paramètres de base dans `config.yaml`

## 🏃‍♂️ Utilisation

```bash
python src/main.py
```

## 📊 Structure du Projet

```
PegaZeus-v1/
├── src/
│   ├── interface/        # Interface utilisateur
│   ├── core/            # Logique métier
│   ├── data/            # Gestion des données
│   └── tests/           # Tests unitaires
├── docs/                # Documentation
├── requirements.txt     # Dépendances
└── README.md           # Documentation principale
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/amazing_feature`)
3. Commit les changements (`git commit -m 'feat: Ajout d'une fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amazing_feature`)
5. Ouvrir une Pull Request

## 📝 License

MIT License - voir le fichier [LICENSE](LICENSE) pour plus de détails.
