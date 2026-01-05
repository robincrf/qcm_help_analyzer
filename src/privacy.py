"""Module de détection et masquage de données personnelles."""

import re
from typing import List, Tuple


class PrivacyFilter:
    """Filtre pour détecter et masquer les données sensibles."""

    # Patterns de détection
    EMAIL_PATTERN = re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    )
    
    PHONE_PATTERN = re.compile(
        r'\b(?:\+33|0)[1-9](?:[\s.-]?\d{2}){4}\b'  # Téléphones français
    )
    
    # Numéros longs (carte bancaire, sécu, etc.)
    LONG_NUMBER_PATTERN = re.compile(
        r'\b\d{13,19}\b'  # 13-19 chiffres consécutifs
    )
    
    # Numéro sécu française (15 chiffres)
    SECU_PATTERN = re.compile(
        r'\b[1-2]\s?\d{2}\s?\d{2}\s?\d{2}\s?\d{3}\s?\d{3}\s?\d{2}\b'
    )
    
    # IBAN
    IBAN_PATTERN = re.compile(
        r'\b[A-Z]{2}\d{2}[A-Z0-9]{1,30}\b'
    )
    
    # Adresse IP
    IP_PATTERN = re.compile(
        r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    )

    def __init__(self, mask_char: str = "█"):
        """
        Initialise le filtre de confidentialité.

        Args:
            mask_char: Caractère utilisé pour masquer
        """
        self.mask_char = mask_char

    def _mask_match(self, match_text: str, keep_prefix: int = 2) -> str:
        """
        Masque un texte en conservant un préfixe.

        Args:
            match_text: Texte à masquer
            keep_prefix: Nombre de caractères à conserver au début

        Returns:
            Texte masqué
        """
        if len(match_text) <= keep_prefix:
            return self.mask_char * len(match_text)
        
        prefix = match_text[:keep_prefix]
        masked_part = self.mask_char * (len(match_text) - keep_prefix)
        return f"{prefix}{masked_part}"

    def detect_sensitive_data(self, text: str) -> List[Tuple[str, str]]:
        """
        Détecte les données sensibles dans le texte.

        Args:
            text: Texte à analyser

        Returns:
            Liste de tuples (type, valeur détectée)
        """
        findings = []

        # Emails
        for match in self.EMAIL_PATTERN.finditer(text):
            findings.append(("EMAIL", match.group()))

        # Téléphones
        for match in self.PHONE_PATTERN.finditer(text):
            findings.append(("PHONE", match.group()))

        # Numéros longs
        for match in self.LONG_NUMBER_PATTERN.finditer(text):
            findings.append(("LONG_NUMBER", match.group()))

        # Sécu
        for match in self.SECU_PATTERN.finditer(text):
            findings.append(("SECU", match.group()))

        # IBAN
        for match in self.IBAN_PATTERN.finditer(text):
            findings.append(("IBAN", match.group()))

        # IP
        for match in self.IP_PATTERN.finditer(text):
            findings.append(("IP", match.group()))

        return findings

    def anonymize_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Anonymise le texte en masquant les données sensibles.

        Args:
            text: Texte à anonymiser

        Returns:
            Tuple (texte anonymisé, liste des types de données masquées)
        """
        anonymized = text
        masked_types = set()

        # Masquer les emails
        for match in self.EMAIL_PATTERN.finditer(text):
            masked = self._mask_match(match.group(), keep_prefix=2)
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("EMAIL")

        # Masquer les téléphones
        for match in self.PHONE_PATTERN.finditer(text):
            masked = self._mask_match(match.group(), keep_prefix=3)
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("PHONE")

        # Masquer les numéros sécu
        for match in self.SECU_PATTERN.finditer(text):
            masked = self.mask_char * len(match.group())
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("SECU")

        # Masquer les numéros longs
        for match in self.LONG_NUMBER_PATTERN.finditer(text):
            masked = self._mask_match(match.group(), keep_prefix=4)
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("LONG_NUMBER")

        # Masquer les IBAN
        for match in self.IBAN_PATTERN.finditer(text):
            masked = self._mask_match(match.group(), keep_prefix=4)
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("IBAN")

        # Masquer les IP (optionnel, peut être désactivé)
        for match in self.IP_PATTERN.finditer(text):
            masked = self._mask_match(match.group(), keep_prefix=3)
            anonymized = anonymized.replace(match.group(), masked)
            masked_types.add("IP")

        return anonymized, list(masked_types)


def filter_sensitive_data(text: str, enabled: bool = True) -> Tuple[str, List[str]]:
    """
    Fonction utilitaire pour filtrer les données sensibles.

    Args:
        text: Texte à filtrer
        enabled: Active le filtrage

    Returns:
        Tuple (texte filtré, types de données masquées)
    """
    if not enabled:
        return text, []
    
    privacy_filter = PrivacyFilter()
    return privacy_filter.anonymize_text(text)
