# CookiNUMnetwork

Application de formation culinaire à distance utilisant des caméras GoPro pour l'enregistrement et la revue de vidéos.

⚠️ Disclaimer : L'application est en cours de développement. Il n'est pas encore possible de cloner le projet pour le tester.

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

## 📝 Fonctionnalités principales

- Streaming vidéo RTMP depuis les caméras GoPro
- Appairage par QR code
- Reconnaissance vocale pour le contrôle
- Système de tagging vidéo
- Raccourcis clavier pour un contrôle rapide

## 🎤 Commandes vocales

Pour utiliser les commandes vocales, commencez toujours par dire "application" ou "logiciel". Voici les commandes disponibles :

Commande vocale : action associée

### Contrôle de la lecture
- "application lecture" : lecture
- "application pause" : Pause
- "application avancer" : Avancer
- "application reculer" : Reculer

### Modes
- "application mode direct" : Mode direct
- "application mode relecture" : Mode révision

### Enregistrement
- "application démarrer enregistrement" : Démarrer l'enregistrement
- "application arrêter enregistrement" : Arrêter l'enregistrement

### Tags
- "application ajouter un tag" : Ajouter un tag à la position actuelle
- "application naviguer au tag [numéro]" : N au tag spécifié (ex: "application aller au tag vingt")

### Fichiers
- "application ouvrir une vidéo" : Ouvrir un fichier vidéo

## ⌨️ Raccourcis clavier

L'application propose plusieurs raccourcis clavier pour faciliter son utilisation :

### Contrôle de la lecture
- `Espace` : Lecture/Pause
- `Flèche droite` : Avancer de 10 secondes
- `Flèche gauche` : Reculer de 10 secondes

### Modes
- `D` : Passer en mode direct
- `R` : Passer en mode révision

### Enregistrement
- `E` : Démarrer/Arrêter l'enregistrement

### Tags
- `T` : Ajouter un tag à la position actuelle

### Fichiers
- `Ctrl + O` : Ouvrir un fichier vidéo

## 🔧 Configuration

L'application est configurée pour fonctionner entièrement en local. La seule connexion réseau requise est celle avec la caméra GoPro via RTMP.