# QCM Screen Analyzer

Application Python pour capturer automatiquement des QCM à l'écran, extraire le texte par OCR et obtenir les réponses via IA.

## ✨ Fonctionnalités

- **Capture d'écran automatique** : Appuyez sur `=` pour capturer
- **OCR en ligne** : Extraction de texte via OCRSpace API (gratuit)
- **Analyse IA** : Réponses aux QCM via Groq API (gratuit)
- **Popup de résultats** : Affichage des réponses dans une fenêtre contextuelle
- **Aucune sauvegarde** : Pas de données écrites sur le disque

## Prérequis

- **Python 3.11+** (testé sur Python 3.14)
- **macOS** (ou Windows/Linux avec adaptations)
- Compte gratuit [OCRSpace](https://ocr.space/ocrapi) pour l'OCR
- Compte gratuit [Groq](https://console.groq.com) pour l'IA

## Installation

### 1. Cloner le projet

```bash
git clone https://github.com/robincrf/qcm_easy.git
cd qcm_easy
cd tests
```

### 2. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate  # Sur macOS/Linux
# venv\Scripts\activate   # Sur Windows
```

### 3. Installer les dépendances

```bash
cd ../
pip install -r requirements.txt
```

## Configuration

### 1. Créer le fichier `.env`

Copiez le fichier d'exemple :

```bash
cp .env.example .env
```

### 2. Obtenir les clés API gratuites

#### **OCRSpace API** (pour l'OCR)
1. Allez sur https://ocr.space/ocrapi
2. Inscrivez-vous gratuitement
3. Copiez votre clé API
4. Quota gratuit : **25,000 requêtes/mois**

#### **Groq API** (pour l'IA)
1. Allez sur https://console.groq.com
2. Créez un compte
3. Générez une clé API
4. Quota gratuit : **30 requêtes/minute**, **14,400/jour**

### 3. Configurer le fichier `.env`

Ouvrez le fichier `.env` et ajoutez vos clés :

```bash
# Configuration OCRSpace API (obligatoire)
OCRSPACE_API_KEY=votre_clé_ocrspace_ici
OCR_LANGUAGE=fre

# Configuration Groq API (obligatoire pour l'analyse IA)
USE_LLM=true
GROQ_API_KEY=votre_clé_groq_ici

# Mode debug (optionnel)
DEBUG_MODE=false
DEBUG_SAVE_SCREENSHOTS=false
```

**Exemple de fichier `.env` configuré :**

```bash
OCRSPACE_API_KEY=K87654321
OCR_LANGUAGE=fre
USE_LLM=true
GROQ_API_KEY=gsk_abc123xyz456
DEBUG_MODE=false
DEBUG_SAVE_SCREENSHOTS=false
```

### 4. Vérifier la configuration

Assurez-vous que :
- Le fichier `.env` existe dans le dossier racine
- Les deux clés API sont correctement copiées (sans espaces)
- `USE_LLM=true` pour activer l'analyse IA
- Le fichier `.env` n'est **PAS** committé sur Git (déjà dans `.gitignore`)

##  Utilisation

### Lancer l'application

```bash
python main.py
```

Vous verrez :

```
 QCM Screen Analyzer démarré
   OCR: OCRSpace API (fre)
   LLM: Groq API (llama-3.3-70b-versatile)
   Mode debug: ✗ Désactivé

 Raccourcis:
   = - Capturer l'écran et analyser
   ESC - Quitter l'application

En attente...
```

### Utiliser l'application

1. **Appuyez sur `=`** pour capturer l'écran complet
2. L'OCR extrait le texte du QCM
3. L'IA analyse et trouve les réponses
4. Une **popup** s'affiche avec les résultats
5. **Appuyez sur ESC** pour quitter

##  Structure du projet

```
qcm-screen-analyzer/
├── src/
│   ├── capture.py       # Capture d'écran (mss)
│   ├── ocr_api.py       # OCR via OCRSpace API
│   └── llm_client.py    # Client IA Groq
├── tests/               # Tests unitaires
├── main.py              # Point d'entrée
├── requirements.txt     # Dépendances
├── .env.example         # Template de configuration
├── .env                 # Votre configuration (NON commité)
├── .gitignore           # Fichiers ignorés par Git
└── README.md            # Ce fichier
```

##  Sécurité

-  Les clés API sont dans `.env` (ignoré par Git)
-  Aucune sauvegarde de captures d'écran par défaut
-  Pas de logs sensibles
-  Timeouts réseau configurés
-  **Ne partagez JAMAIS votre fichier `.env`**

##  Dépannage

### "Clé API OCRSpace manquante"
 Vérifiez que `OCRSPACE_API_KEY` est dans `.env`

### "Groq API key manquante"
 Vérifiez que `GROQ_API_KEY` est dans `.env` et `USE_LLM=true`

### "Erreur OCRSpace: File size exceeds"
 L'image est automatiquement compressée, vérifiez votre connexion

### Rate limit dépassé
 Groq gratuit : max 30 req/min. Attendez quelques secondes.

### Permissions macOS
 Autorisez Terminal dans **Préférences Système > Confidentialité > Accessibilité**

##  Limites gratuites

| Service | Limite gratuite |
|---------|----------------|
| **OCRSpace** | 25,000 requêtes/mois |
| **Groq** | 30 req/min, 14,400/jour |

##  License

MIT License - Libre d'utilisation

##  Contribution

Les contributions sont les bienvenues ! Ouvrez une issue ou un PR.

---

**Note** : Cette application est destinée à un usage personnel éducatif. Respectez les conditions d'utilisation des API tierces.
