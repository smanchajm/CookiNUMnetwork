# Guide d'Installation CookiNUMnetwork

## 📋 Prérequis

### VLC Media Player
CookiNUMnetwork nécessite **VLC Media Player** pour la lecture des vidéos. Assurez-vous d'installer la version correspondant à votre système d'exploitation :

- **Windows** : [Télécharger VLC pour Windows](https://www.videolan.org/vlc/download-windows.html)
- **macOS** : [Télécharger VLC pour macOS](https://www.videolan.org/vlc/download-macosx.html)

> ⚠️ **Important** : Si vous rencontrez des erreurs lors du lancement de l'application liées à VLC, vérifiez que vous avez bien installé la bonne version pour votre système d'exploitation.

### Réseau WiFi
Pour utiliser le streaming vidéo avec votre caméra GoPro :

- **Même réseau WiFi** : Votre ordinateur et votre caméra GoPro doivent être connectés au même réseau WiFi

## 🪟 Installation sur Windows

### Installation de l'application

1. **Téléchargez** le fichier d'installation `.exe` de CookiNUMnetwork
2. **Double-cliquez** sur le fichier d'installation pour lancer l'assistant
3. **L'installateur vous proposera** de choisir entre :
   - **Installation pour l'utilisateur actuel** (recommandé si vous n'avez pas les droits administrateur)
   - **Installation pour tous les utilisateurs** (recommandé avec droits administrateur)
4. **Suivez** les instructions de l'assistant d'installation

### Choix d'installation recommandé

#### Installation pour tous les utilisateurs (avec droits administrateur)
- **Avantages** : Configure automatiquement les règles de pare-feu nécessaires pour le streaming vidéo
- **Recommandé** : Pour une utilisation optimale et une configuration automatique du réseau

#### Installation pour l'utilisateur actuel
- **Utilisation** : Si vous n'avez pas les droits administrateur
- **Limitation** : Nécessite une configuration manuelle des règles de pare-feu

### Configuration du pare-feu Windows

Si vous rencontrez des problèmes de streaming, vérifiez que les règles de pare-feu suivantes sont configurées :

#### Règles automatiques (installation pour tous les utilisateurs)
L'installation pour tous les utilisateurs configure automatiquement :
- **CookiNUMnetwork** : Accès entrant et sortant
- **MediaMTX** : Accès entrant et sortant sur le port 1935

#### Configuration manuelle (si nécessaire)
Si vous avez choisi l'installation pour l'utilisateur actuel, demandez à votre service informatique d'ajouter ces règles :

**Autorisations nécessaires pour le pare-feu Windows :**

**Ports utilisés :**
- **Port 1935** : Pour recevoir le flux RTMP de la GoPro vers le serveur local
- **Port 8554** : Pour la communication RTSP entre le serveur et CookiNUMnetwork (plus performant)

1. **Application principale CookiNUMnetwork** :
   - Autoriser les connexions entrantes et sortantes pour `CookiNUMnetwork.exe`

2. **Serveur de streaming MediaMTX** :
   - Autoriser les connexions entrantes et sortantes pour `mediamtx.exe`
   - Localisation : `[Dossier_Installation]\_internal\src\resources\binaries\mediamtx\mediamtx.exe`

**Commandes PowerShell :**
```powershell
# Règles pour l'application principale CookiNUMnetwork (TCP et UDP)
New-NetFirewallRule -DisplayName "CookiNUMnetwork TCP" -Direction Inbound -Program "C:\Program Files\CookiNUMnetwork\CookiNUMnetwork.exe" -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "CookiNUMnetwork UDP" -Direction Inbound -Program "C:\Program Files\CookiNUMnetwork\CookiNUMnetwork.exe" -Protocol UDP -Action Allow

# Règles pour le serveur de streaming MediaMTX (TCP et UDP)
New-NetFirewallRule -DisplayName "MediaMTX TCP" -Direction Inbound -Program "C:\Program Files\CookiNUMnetwork\_internal\src\resources\binaries\mediamtx\mediamtx.exe" -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "MediaMTX UDP" -Direction Inbound -Program "C:\Program Files\CookiNUMnetwork\_internal\src\resources\binaries\mediamtx\mediamtx.exe" -Protocol UDP -Action Allow
```

> ⚠️ **Important** : Adaptez les chemins dans les commandes selon votre dossier d'installation :
> - Pour une installation "tous les utilisateurs" : `C:\Program Files\CookiNUMnetwork\`
> - Pour une installation "utilisateur actuel" : `C:\Users\[NomUtilisateur]\AppData\Local\Programs\CookiNUMnetwork\`

## 🍎 Installation sur macOS

### Installation de l'application

1. **Téléchargez** le fichier `.zip` de CookiNUMnetwork
2. **Double-cliquez** sur le fichier `.zip` pour l'extraire
3. **Ouvrez** le dossier extrait contenant l'application CookiNUMnetwork.app

> ⚠️ **Important** : Ne déplacez pas l'application vers le dossier Applications car elle n'est pas signée. Gardez-la dans le dossier d'extraction pour éviter les problèmes de permissions.

### Première exécution

Lors du premier lancement, macOS peut afficher un avertissement de sécurité :

1. **Double-cliquez** sur l'application dans le dossier d'extraction
2. Si un message indique que le développeur n'est pas identifié :
   - Cliquez sur **"Fermer"**
   - **Clic droit** sur l'application et sélectionnez **"Ouvrir"**
   - Cliquez sur **"Ouvrir"** dans la boîte de dialogue qui apparaît
3. **Répétez** cette opération si nécessaire jusqu'à ce que l'application se lance

### Configuration des autorisations

Si vous n'avez pas les droits administrateur, demandez à votre administrateur système de :
- Vérifier l'application dans les paramètres de sécurité
- Autoriser l'accès réseau pour CookiNUMnetwork

## 🔧 Dépannage

### Problèmes courants

#### Erreur VLC au lancement
**Symptôme** : L'application affiche une erreur liée à VLC
**Solution** : 
- Vérifiez que VLC est installé et à jour
- Assurez-vous d'avoir la bonne version pour votre système d'exploitation
- Redémarrez l'application après l'installation de VLC

#### Problèmes de streaming
**Symptôme** : Le streaming ne fonctionne pas, aucune vidéo ne s'affiche
**Solution** :

1. **Vérifiez le port 1935** :
   ```cmd
   # Windows
   netstat -an | findstr 1935
   
   # macOS/Linux
   netstat -an | grep 1935
   ```
   Si vous voyez "LISTENING" ou "LISTEN", l'application est bien lancée.

2. **Vérifiez le pare-feu** :
   - Désactivez temporairement le pare-feu Windows/macOS
   - Testez le streaming
   - Si ça fonctionne, le problème vient du pare-feu

3. **Vérifiez l'antivirus** :
   - Désactivez temporairement votre antivirus
   - Testez le streaming
   - Si ça fonctionne, ajoutez CookiNUMnetwork aux exceptions de votre antivirus

**Symptôme** : Problèmes non identifiés
- Consultez les logs de l'application
- Pour localiser les logs : ouvrez une vidéo dans l'application, puis remontez d'un niveau dans le dossier pour trouver le fichier de logs

## 🔒 Sécurité

CookiNUMnetwork est une application **locale** qui :
- Stocke toutes les données localement
- Se connecte uniquement aux caméras GoPro via RTMP sur le port 1935

Les règles de pare-feu sont nécessaires uniquement pour permettre la communication avec les caméras GoPro sur votre réseau local.
