"""Tests pour le module OCR."""

import pytest
from PIL import Image, ImageDraw, ImageFont
from src.ocr import OCRProcessor, extract_text_from_image


class TestOCRProcessor:
    """Tests pour la classe OCRProcessor."""

    def test_ocr_processor_init(self):
        """Test l'initialisation du processeur OCR."""
        processor = OCRProcessor(lang="eng", min_text_length=20)
        assert processor.lang == "eng"
        assert processor.min_text_length == 20

    def test_preprocess_image(self):
        """Test le prétraitement d'image."""
        # Créer une image de test
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 80), "Test Text", fill='black')

        processor = OCRProcessor()
        preprocessed = processor.preprocess_image(img)

        # Vérifier que l'image est en niveaux de gris
        assert preprocessed.mode == 'L'
        # Vérifier que les dimensions sont conservées
        assert preprocessed.size == img.size

    def test_extract_text_short_text(self):
        """Test l'extraction avec texte trop court."""
        # Créer une image avec peu de texte
        img = Image.new('RGB', (200, 100), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 40), "AB", fill='black')

        processor = OCRProcessor(min_text_length=30)
        text, success = processor.extract_text(img)

        # Le texte est trop court, success devrait être False
        assert success is False

    def test_extract_text_no_preprocessing(self):
        """Test l'extraction sans prétraitement."""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 80), "Test extraction without preprocessing", fill='black')

        processor = OCRProcessor(min_text_length=10)
        text, success = processor.extract_text(img, preprocess=False)

        # Devrait au moins retourner quelque chose
        assert isinstance(text, str)
        assert isinstance(success, bool)


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires."""

    def test_extract_text_from_image(self):
        """Test la fonction utilitaire extract_text_from_image."""
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        draw.text((50, 80), "This is a longer text for testing purposes", fill='black')

        text, success = extract_text_from_image(img, lang="eng", min_length=20)

        assert isinstance(text, str)
        assert isinstance(success, bool)
