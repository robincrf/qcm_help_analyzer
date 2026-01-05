"""Tests pour le module de confidentialité."""

import pytest
from src.privacy import PrivacyFilter, filter_sensitive_data


class TestPrivacyFilter:
    """Tests pour la classe PrivacyFilter."""

    def test_privacy_filter_init(self):
        """Test l'initialisation du filtre."""
        pf = PrivacyFilter(mask_char="*")
        assert pf.mask_char == "*"

    def test_detect_email(self):
        """Test la détection d'emails."""
        pf = PrivacyFilter()
        text = "Contactez-moi à john.doe@example.com pour plus d'infos."
        
        findings = pf.detect_sensitive_data(text)
        
        assert len(findings) > 0
        assert any(finding[0] == "EMAIL" for finding in findings)
        assert any("john.doe@example.com" in finding[1] for finding in findings)

    def test_detect_phone_french(self):
        """Test la détection de numéros de téléphone français."""
        pf = PrivacyFilter()
        text = "Appelez-moi au 06 12 34 56 78"
        
        findings = pf.detect_sensitive_data(text)
        
        # Devrait détecter le téléphone
        assert len(findings) > 0
        assert any(finding[0] == "PHONE" for finding in findings)

    def test_detect_long_numbers(self):
        """Test la détection de numéros longs (carte bancaire, etc.)."""
        pf = PrivacyFilter()
        text = "Ma carte: 1234567890123456"
        
        findings = pf.detect_sensitive_data(text)
        
        assert len(findings) > 0
        assert any(finding[0] == "LONG_NUMBER" for finding in findings)

    def test_detect_ip_address(self):
        """Test la détection d'adresses IP."""
        pf = PrivacyFilter()
        text = "Le serveur est à 192.168.1.100"
        
        findings = pf.detect_sensitive_data(text)
        
        assert len(findings) > 0
        assert any(finding[0] == "IP" for finding in findings)

    def test_anonymize_email(self):
        """Test l'anonymisation d'emails."""
        pf = PrivacyFilter()
        text = "Contactez john.doe@example.com"
        
        anonymized, types = pf.anonymize_text(text)
        
        assert "john.doe@example.com" not in anonymized
        assert "EMAIL" in types
        # Devrait commencer par "jo" (keep_prefix=2)
        assert "jo" in anonymized

    def test_anonymize_phone(self):
        """Test l'anonymisation de téléphones."""
        pf = PrivacyFilter()
        text = "Téléphone: 0612345678"
        
        anonymized, types = pf.anonymize_text(text)
        
        assert "0612345678" not in anonymized
        assert "PHONE" in types

    def test_anonymize_multiple_types(self):
        """Test l'anonymisation de plusieurs types de données."""
        pf = PrivacyFilter()
        text = "Email: test@mail.com, Tel: 0612345678, IP: 192.168.1.1"
        
        anonymized, types = pf.anonymize_text(text)
        
        # Vérifier que tous les types sont détectés
        assert "EMAIL" in types
        assert "PHONE" in types
        assert "IP" in types
        
        # Vérifier que les données originales ne sont plus présentes
        assert "test@mail.com" not in anonymized
        assert "0612345678" not in anonymized

    def test_mask_match(self):
        """Test la fonction de masquage."""
        pf = PrivacyFilter(mask_char="*")
        
        masked = pf._mask_match("1234567890", keep_prefix=4)
        assert masked == "1234******"
        
        masked = pf._mask_match("AB", keep_prefix=2)
        assert masked == "**"


class TestUtilityFunctions:
    """Tests pour les fonctions utilitaires."""

    def test_filter_sensitive_data_enabled(self):
        """Test le filtrage avec le mode activé."""
        text = "Mon email: user@example.com"
        
        filtered, types = filter_sensitive_data(text, enabled=True)
        
        assert "user@example.com" not in filtered
        assert "EMAIL" in types

    def test_filter_sensitive_data_disabled(self):
        """Test le filtrage avec le mode désactivé."""
        text = "Mon email: user@example.com"
        
        filtered, types = filter_sensitive_data(text, enabled=False)
        
        assert filtered == text  # Pas de modification
        assert types == []

    def test_no_sensitive_data(self):
        """Test avec du texte sans données sensibles."""
        pf = PrivacyFilter()
        text = "Ceci est un texte normal sans données personnelles."
        
        anonymized, types = pf.anonymize_text(text)
        
        assert anonymized == text  # Pas de modification
        assert len(types) == 0
