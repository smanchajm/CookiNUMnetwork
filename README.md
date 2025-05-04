# CookiNUMnetwork

Application de formation culinaire à distance utilisant des caméras GoPro pour l'enregistrement et la revue de vidéos éducatives.

## 🚀 Installation

1. Créer un environnement virtuel Python :
```bash
python -m venv venv
```

2. Activer l'environnement virtuel :
- Windows :
```bash
.\venv\Scripts\activate
```
- Linux/MacOS :
```bash
source venv/bin/activate
```

3. Installer les dépendances :
```bash
pip install -r requirements.txt
```

## 🛠️ Développement

### Structure du projet
```
CookiNUMnetwork/
├── src/
│   ├── core/       # Logique métier principale
│   ├── ui/         # Interface utilisateur PyQt6
│   ├── video/      # Traitement vidéo et RTMP
│   ├── voice/      # Reconnaissance vocale
│   ├── storage/    # Gestion du stockage local
│   └── utils/      # Utilitaires communs
├── tests/          # Tests unitaires et d'intégration
├── docs/           # Documentation technique
└── resources/      # Ressources (images, icônes, etc.)
```

### Outils de développement
- `black` : Formatage de code
- `flake8` : Linting
- `mypy` : Vérification de types
- `pytest` : Tests unitaires

## 📝 Fonctionnalités principales

- Streaming vidéo RTMP depuis les caméras GoPro
- Appairage par QR code
- Reconnaissance vocale pour le contrôle
- Système de tagging vidéo
- Interface utilisateur moderne avec PyQt6

## 🔧 Configuration

L'application est configurée pour fonctionner entièrement en local. La seule connexion réseau requise est celle avec la caméra GoPro via RTMP.

## 📦 Packaging

Pour créer un exécutable :
```bash
pyinstaller --onefile --windowed src/main.py
```

## 📄 Licence

Propriétaire - Tous droits réservés 