# Screen Tutor Assistant 🎓

Application desktop Windows en Python pour analyser des captures d'écran de questions (QCM, exercices) via OCR local et obtenir des explications pédagogiques d'un LLM tuteur.

## 🎯 Fonctionnalités

- **Capture d'écran instantanée** : Appuyez sur `P` pour capturer l'écran complet
- **OCR local** : Extraction de texte avec Tesseract (français + anglais)
- **Mode tuteur intelligent** : Explications et indices sans révéler la réponse immédiatement
- **Interface overlay** : Fenêtre toujours visible avec bouton "Révéler"
- **Mode confidentialité** : Masquage automatique des données personnelles (emails, téléphones, numéros)
- **Sécurité** : Pas de sauvegarde des captures (sauf mode debug), timeouts réseau, gestion d'erreurs

## 📋 Prérequis

### Python
- Python 3.11 ou supérieur
- pip (gestionnaire de paquets Python)

### Tesseract OCR (Windows)

**Option 1 : Installation avec installeur**
1. Téléchargez l'installeur depuis : https://github.com/UB-Mannheim/tesseract/wiki
2. Lancez l'installeur et suivez les instructions
3. **Important** : Cochez "Additional language data (download)" et sélectionnez `fra` (Français)
4. Par défaut, Tesseract s'installe dans `C:\Program Files\Tesseract-OCR`

**Option 2 : Via Chocolatey**
```powershell
choco install tesseract
```

**Vérification de l'installation**
```powershell
tesseract --version
```

Si la commande n'est pas reconnue, ajoutez `C:\Program Files\Tesseract-OCR` au PATH système.

### Clé API LLM
- Clé API OpenAI (recommandé) : https://platform.openai.com/api-keys
- OU tout autre endpoint compatible OpenAI

## 🚀 Installation

### 1. Cloner ou télécharger le projet
```bash
cd screen-tutor-assistant
```

### 2. Créer un environnement virtuel (recommandé)
```powershell
# Windows PowerShell
python -m venv venv
.\venv\Scripts\Activate.ps1

# Windows CMD
python -m venv venv
venv\Scripts\activate.bat
```

### 3. Installer les dépendances Python
```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement
```bash
# Copier le fichier exemple
cp .env.example .env
```

Éditez le fichier `.env` et configurez :
```env
# Configuration LLM
OPENAI_API_KEY=sk-votre-clé-api-ici
LLM_MODEL=gpt-4o-mini

# Configuration OCR
TESSERACT_LANG=fra+eng
OCR_MIN_TEXT_LENGTH=30

# Configuration Réseau
LLM_TIMEOUT=30
LLM_MAX_RETRIES=1

# Mode confidentialité
PRIVACY_MODE=true

# Mode debug (désactiver en production)
DEBUG_MODE=false
DEBUG_SAVE_SCREENSHOTS=false
```

**Configuration avancée** (endpoint personnalisé) :
```env
# Pour utiliser un autre fournisseur compatible OpenAI
LLM_BASE_URL=https://api.votre-fournisseur.com/v1
LLM_API_KEY=votre-clé-api
LLM_MODEL=nom-du-modele
```

### 5. Configuration Tesseract (si nécessaire)

Si Tesseract n'est pas dans le PATH, vous pouvez spécifier le chemin dans le code.

Éditez `src/ocr.py` et ajoutez après les imports :
```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## 📖 Utilisation

### Lancer l'application
```bash
python main.py
```

Vous verrez :
```
🚀 Screen Tutor Assistant démarré
   Mode confidentialité: ✓ Activé
   Mode debug: ✗ Désactivé

📌 Raccourcis:
   P - Capturer l'écran et analyser
   ESC - Quitter l'application

En attente...
```

### Workflow
1. **Affichez votre question** (QCM, exercice) sur l'écran
2. **Appuyez sur `P`** pour capturer
3. L'application :
   - 📸 Capture l'écran
   - 🔍 Extrait le texte via OCR
   - 🔒 Masque les données sensibles (si mode confidentialité activé)
   - 🤖 Envoie au LLM pour obtenir une explication
4. Une **fenêtre overlay** apparaît avec :
   - Le texte OCR extrait
   - L'explication pédagogique + indice
   - Bouton "Révéler la réponse"
5. **Cliquez sur "Révéler"** pour obtenir la réponse finale avec justification
6. **Utilisez les boutons** :
   - 📋 Copier : Copie le contenu dans le presse-papiers
   - ❌ Fermer : Ferme la fenêtre

### Raccourcis clavier
- **P** : Capturer et analyser l'écran
- **ESC** : Quitter l'application

## 🔒 Mode Confidentialité

Le mode confidentialité (activé par défaut) détecte et masque automatiquement :
- ✉️ Emails
- 📱 Numéros de téléphone (format français)
- 💳 Numéros longs (cartes bancaires, etc.)
- 🆔 Numéros de sécurité sociale
- 🏦 IBAN
- 🌐 Adresses IP

**Désactivation** : Mettez `PRIVACY_MODE=false` dans `.env`

## 🐛 Mode Debug

Pour diagnostiquer des problèmes :

1. Activez le mode debug dans `.env` :
```env
DEBUG_MODE=true
DEBUG_SAVE_SCREENSHOTS=true
```

2. Les captures d'écran seront sauvegardées dans `debug_screenshots/`
3. Des messages détaillés seront affichés dans la console

**⚠️ N'oubliez pas de désactiver en production !**

## 🧪 Tests

Exécuter les tests unitaires :
```bash
# Tous les tests
pytest

# Avec verbosité
pytest -v

# Un fichier spécifique
pytest tests/test_privacy.py

# Avec couverture
pytest --cov=src tests/
```

Tests disponibles :
- `test_ocr.py` : Preprocessing et extraction OCR
- `test_privacy.py` : Détection et masquage de données sensibles
- `test_llm_client.py` : Client HTTP avec mocks

## 📁 Structure du Projet

```
screen-tutor-assistant/
├── src/                      # Code source
│   ├── __init__.py
│   ├── capture.py           # Capture d'écran (mss)
│   ├── ocr.py               # OCR avec preprocessing (pytesseract)
│   ├── llm_client.py        # Client LLM (OpenAI compatible)
│   ├── privacy.py           # Filtre de confidentialité
│   └── ui.py                # Interface overlay (tkinter)
├── tests/                    # Tests unitaires
│   ├── test_ocr.py
│   ├── test_privacy.py
│   └── test_llm_client.py
├── main.py                   # Point d'entrée
├── requirements.txt          # Dépendances Python
├── .env.example             # Template configuration
├── .gitignore
└── README.md                # Cette documentation
```

## ⚙️ Configuration Avancée

### Personnaliser l'OCR
Dans `.env` :
```env
# Langues (séparées par +)
TESSERACT_LANG=fra+eng+deu

# Longueur minimale de texte
OCR_MIN_TEXT_LENGTH=50
```

### Personnaliser le LLM
```env
# Timeout (secondes)
LLM_TIMEOUT=60

# Nombre de tentatives
LLM_MAX_RETRIES=2

# Modèle
LLM_MODEL=gpt-4
```

### Modifier le prompt tuteur
Éditez `src/llm_client.py` et modifiez `TUTOR_SYSTEM_PROMPT`.

## 🔧 Dépannage

### Erreur "Tesseract not found"
- Vérifiez que Tesseract est installé : `tesseract --version`
- Ajoutez le chemin dans le PATH ou spécifiez-le dans `src/ocr.py`

### Erreur "API key manquante"
- Vérifiez que le fichier `.env` existe
- Vérifiez que `OPENAI_API_KEY` est défini dans `.env`

### Texte OCR vide ou incomplet
- Augmentez la résolution de votre écran
- Zoomez sur le texte avant de capturer
- Assurez-vous que le texte est net et contrasté
- Vérifiez que les langues sont bien installées pour Tesseract

### Hotkey ne fonctionne pas
- Exécutez le script avec les privilèges administrateur (certains hotkeys globaux le requièrent)
- Vérifiez qu'aucune autre application n'utilise la touche `P`

### Timeout LLM
- Augmentez `LLM_TIMEOUT` dans `.env`
- Vérifiez votre connexion Internet
- Vérifiez que votre clé API est valide

## 📝 Limitations

- **Windows uniquement** : L'application est optimisée pour Windows (keyboard, mss)
- **Tesseract requis** : OCR local nécessite une installation séparée de Tesseract
- **Hotkey global** : Peut nécessiter des privilèges administrateur
- **Précision OCR** : Dépend de la qualité de la capture (résolution, contraste)

## 🛡️ Sécurité & Confidentialité

- ✅ Pas de sauvegarde des captures (sauf mode debug)
- ✅ Masquage automatique des données personnelles
- ✅ Variables d'environnement pour les clés API
- ✅ Timeouts réseau configurables
- ✅ Gestion des erreurs et exceptions
- ✅ Logs minimaux (pas de données sensibles loggées)

## 📜 Licence

Ce projet est fourni "tel quel" à des fins éducatives.

## 🤝 Contribution

Pour contribuer :
1. Forkez le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Committez vos changements (`git commit -m 'Add AmazingFeature'`)
4. Pushez vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📞 Support

En cas de problème :
1. Consultez la section **Dépannage** ci-dessus
2. Activez le mode debug pour plus d'informations
3. Vérifiez que toutes les dépendances sont installées
4. Ouvrez une issue sur GitHub avec les logs

---

**Développé avec ❤️ pour faciliter l'apprentissage**
