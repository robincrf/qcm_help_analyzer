"""Module OCR avec preprocessing d'image."""

from typing import Optional, Tuple
from PIL import Image, ImageEnhance, ImageOps
import pytesseract


class OCRProcessor:
    """Processeur OCR avec prétraitement d'image."""

    def __init__(
        self,
        lang: str = "fra+eng",
        min_text_length: int = 30,
        tesseract_cmd: Optional[str] = None
    ):
        """
        Initialise le processeur OCR.

        Args:
            lang: Langues pour Tesseract (ex: 'fra+eng')
            min_text_length: Longueur minimale de texte acceptable
            tesseract_cmd: Chemin vers l'exécutable Tesseract (optionnel)
        """
        self.lang = lang
        self.min_text_length = min_text_length
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Prétraite l'image pour améliorer l'OCR.

        Opérations:
        - Conversion en niveaux de gris
        - Augmentation du contraste
        - Binarisation optionnelle

        Args:
            image: Image PIL à prétraiter

        Returns:
            Image prétraitée
        """
        # Conversion en niveaux de gris
        gray_image = ImageOps.grayscale(image)

        # Augmentation du contraste
        enhancer = ImageEnhance.Contrast(gray_image)
        contrast_image = enhancer.enhance(2.0)

        # Augmentation de la netteté
        sharpness_enhancer = ImageEnhance.Sharpness(contrast_image)
        sharp_image = sharpness_enhancer.enhance(1.5)

        # Binarisation (conversion en noir et blanc pur)
        # Utiliser un seuil adaptatif
        threshold = 128
        binary_image = sharp_image.point(lambda p: p > threshold and 255)

        return binary_image

    def extract_text(
        self,
        image: Image.Image,
        preprocess: bool = True
    ) -> Tuple[str, bool]:
        """
        Extrait le texte d'une image via OCR.

        Args:
            image: Image PIL à traiter
            preprocess: Appliquer le prétraitement

        Returns:
            Tuple (texte extrait, succès)
            succès = False si le texte est trop court
        """
        try:
            # Prétraitement si demandé
            if preprocess:
                processed_image = self.preprocess_image(image)
            else:
                processed_image = image

            # Extraction OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang=self.lang,
                config='--psm 6'  # PSM 6: bloc de texte uniforme
            )

            # Nettoyage du texte
            text = text.strip()

            # Vérification longueur minimale
            if len(text) < self.min_text_length:
                return text, False

            return text, True

        except Exception as e:
            print(f"Erreur lors de l'OCR: {e}")
            return "", False


def extract_text_from_image(
    image: Image.Image,
    lang: str = "fra+eng",
    min_length: int = 30
) -> Tuple[str, bool]:
    """
    Fonction utilitaire pour extraire du texte d'une image.

    Args:
        image: Image PIL
        lang: Langues Tesseract
        min_length: Longueur minimale requise

    Returns:
        Tuple (texte, succès)
    """
    processor = OCRProcessor(lang=lang, min_text_length=min_length)
    return processor.extract_text(image)
