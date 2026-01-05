"""Client pour Groq LLM API."""

import os
from typing import Optional
import requests


class LLMClient:
    """Client pour interagir avec l'API Groq."""

    # Prompt pour analyse de QCM
    QCM_PROMPT = """Tu es un assistant expert qui analyse des QCM (questions à choix multiples).

Voici le texte extrait d'un QCM. Analyse-le et :
1. Identifie TOUTES les questions
2. Liste les options de réponse pour chaque question
3. Pour CHAQUE question, détermine la RÉPONSE CORRECTE
4. Donne une EXPLICATION COURTE pour chaque réponse

Format de réponse souhaité :

❓ QUESTION 1: [texte de la question]
Options:
A) [option A]
B) [option B]
C) [option C]
D) [option D]

✅ RÉPONSE: [lettre]
💡 EXPLICATION: [explication courte et claire]

---

❓ QUESTION 2: ...
[etc.]

Si le texte ne contient pas de QCM identifiable, indique-le clairement."""

    def __init__(self, api_key: Optional[str] = None, model: str = "llama-3.3-70b-versatile"):
        """
        Initialise le client Groq.

        Args:
            api_key: Clé API Groq (ou depuis variable GROQ_API_KEY)
            model: Modèle à utiliser
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Clé API Groq manquante!\n\n"
                "Obtenez une clé gratuite sur https://console.groq.com\n"
                "Puis ajoutez-la dans .env:\n"
                "GROQ_API_KEY=votre_clé_ici"
            )
        
        self.model = model
        self.base_url = "https://api.groq.com/openai/v1"

    def analyze_qcm_text(self, text: str) -> Optional[str]:
        """
        Analyse un texte de QCM avec Groq.

        Args:
            text: Texte extrait du QCM

        Returns:
            Réponse formatée avec questions et réponses, ou None en cas d'erreur
        """
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": self.QCM_PROMPT
                },
                {
                    "role": "user",
                    "content": f"Voici le texte du QCM à analyser:\n\n{text}"
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            answer = data.get("choices", [{}])[0].get("message", {}).get("content")
            return answer

        except requests.exceptions.Timeout:
            print("⏱️  Timeout - la requête a pris trop de temps")
            return None

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                print("❌ Clé API Groq invalide")
            elif e.response.status_code == 429:
                print("⚠️  Limite de requêtes atteinte - attendez quelques secondes")
            else:
                print(f"❌ Erreur HTTP {e.response.status_code}: {e}")
            return None

        except Exception as e:
            print(f"❌ Erreur lors de l'analyse: {e}")
            return None


def create_llm_client(api_key: Optional[str] = None) -> LLMClient:
    """
    Factory function pour créer un client Groq.

    Args:
        api_key: Clé API Groq (optionnel, lecture depuis .env par défaut)

    Returns:
        Instance de LLMClient

    Raises:
        ValueError: Si la clé API est manquante
    """
    return LLMClient(api_key=api_key)
