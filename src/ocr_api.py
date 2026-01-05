"""Module OCR via API OCRSpace (gratuit)."""

import os
import base64
from typing import Optional, Tuple
from PIL import Image
import requests
import io


class OCRSpaceAPI:
    """Client pour l'API OCRSpace gratuite."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        language: str = "fre"
    ):
        """
        Initialise le client OCRSpace.

        Args:
            api_key: Clé API OCRSpace (gratuite sur ocr.space/ocrapi)
            language: Code langue (fre=français, eng=anglais)
        """
        self.api_key = api_key or os.getenv("OCRSPACE_API_KEY")
        self.language = language
        self.api_url = "https://api.ocr.space/parse/image"
        
        if not self.api_key:
            raise ValueError(
                "Clé API OCRSpace manquante.\n"
                "Obtenez-en une gratuitement sur: https://ocr.space/ocrapi\n"
                "Puis ajoutez OCRSPACE_API_KEY dans .env"
            )

    def _image_to_base64(self, image: Image.Image) -> str:
        """
        Convertit une image PIL en base64 avec compression.

        Args:
            image: Image PIL

        Returns:
            String base64
        """
        buffered = io.BytesIO()
        
        # Redimensionner si trop grande
        max_size = (1920, 1080)
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            print(f"   Image redimensionnée à {image.size}")
        
        # Sauvegarder avec compression
        image.save(buffered, format="JPEG", quality=85, optimize=True)
        size_kb = buffered.tell() / 1024
        
        # Si toujours trop gros, réduire la qualité
        if size_kb > 900:  # Marge de sécurité
            buffered = io.BytesIO()
            image.save(buffered, format="JPEG", quality=70, optimize=True)
            size_kb = buffered.tell() / 1024
            print(f"   Image compressée à {size_kb:.1f} KB")
        
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def extract_text(self, image: Image.Image) -> Tuple[str, bool]:
        """
        Extrait le texte d'une image via OCRSpace API.

        Args:
            image: Image PIL à analyser

        Returns:
            Tuple (texte extrait, succès)
        """
        try:
            # Convertir l'image en base64
            image_b64 = self._image_to_base64(image)

            # Préparer la requête
            payload = {
                'apikey': self.api_key,
                'language': self.language,
                'isOverlayRequired': False,
                'base64Image': f'data:image/jpeg;base64,{image_b64}',
                'OCREngine': 2  # Moteur 2 est plus précis
            }

            print(f"📤 Envoi à OCRSpace API...")
            
            # Envoyer la requête
            response = requests.post(
                self.api_url,
                data=payload,
                timeout=30
            )
            response.raise_for_status()

            # Parser la réponse
            result = response.json()

            # Vérifier les erreurs
            if result.get('IsErroredOnProcessing'):
                error_msg = result.get('ErrorMessage', ['Erreur inconnue'])[0]
                print(f"❌ Erreur OCRSpace: {error_msg}")
                return "", False

            # Extraire le texte
            parsed_results = result.get('ParsedResults', [])
            if not parsed_results:
                print("⚠️  Aucun texte détecté")
                return "", False

            text = parsed_results[0].get('ParsedText', '').strip()

            if not text:
                print("⚠️  Texte vide")
                return "", False

            print(f"✓ Texte extrait: {len(text)} caractères")
            return text, True

        except requests.exceptions.Timeout:
            print("❌ Timeout de l'API OCRSpace")
            return "", False

        except requests.exceptions.RequestException as e:
            print(f"❌ Erreur réseau: {e}")
            return "", False

        except Exception as e:
            print(f"❌ Erreur inattendue: {e}")
            return "", False


def extract_text_from_image_api(
    image: Image.Image,
    api_key: Optional[str] = None,
    language: str = "fre"
) -> Tuple[str, bool]:
    """
    Fonction utilitaire pour extraire du texte via OCRSpace.

    Args:
        image: Image PIL
        api_key: Clé API OCRSpace
        language: Langue (fre, eng, etc.)

    Returns:
        Tuple (texte, succès)
    """
    ocr = OCRSpaceAPI(api_key=api_key, language=language)
    return ocr.extract_text(image)
