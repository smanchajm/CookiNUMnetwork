# CookiNUMnetwork

Application de formation culinaire à distance utilisant des caméras GoPro pour l'enregistrement et la revue de vidéos.

## 🛠️ Développement

## 📝 Fonctionnalités principales

- Streaming vidéo RTMP depuis les caméras GoPro
- Appairage par QR code
- Reconnaissance vocale pour le contrôle
- Système de tagging vidéo
- Raccourcis clavier pour un contrôle rapide

## 🎤 Commandes vocales

Pour utiliser les commandes vocales, commencez toujours par dire "caméra" "application" ou "logiciel". Voici les commandes disponibles :

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
- "application ajouter un tag" :  un tag à la position actuelle
- "application aller au tag [numéro]" : N au tag spécifié (ex: "application aller au tag cinq")

### Fichiers
- "application ouvrir une vidéo" : Ouvrir un fichier vidéo
- "application lire la dernière vidéo": Ouvrir la dernière vidéo enregistrée

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
- `O` : Ouvrir un fichier vidéo

## 🔧 Configuration

L'application est configurée pour fonctionner entièrement en local. La seule connexion réseau requise est celle avec la caméra GoPro via RTMP.