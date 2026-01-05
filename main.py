"""Point d'entrée principal de l'application Screen Tutor Assistant (version terminal)."""

import os
import sys
import threading
import subprocess
from typing import Optional
from dotenv import load_dotenv
from pynput import keyboard as kb

# Import des modules locaux
from src.capture import capture_screen
from src.ocr_api import OCRSpaceAPI
from src.llm_client import create_llm_client


class ScreenTutorApp:
    """Application principale Screen Tutor Assistant."""

    def __init__(self):
        """Initialise l'application."""
        # Charger les variables d'environnement
        load_dotenv()

        # Configuration
        self.debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.debug_save = os.getenv("DEBUG_SAVE_SCREENSHOTS", "false").lower() == "true"
        self.ocr_lang = os.getenv("OCR_LANGUAGE", "fre")
        self.use_llm = os.getenv("USE_LLM", "false").lower() == "true"

        # Composants
        self.ocr_api = OCRSpaceAPI(language=self.ocr_lang)
        
        # LLM optionnel (si activé)
        self.llm_client = None
        if self.use_llm:
            try:
                self.llm_client = create_llm_client()
                print("   LLM: ✓ Activé (Groq API)")
            except Exception as e:
                print(f"   LLM: ✗ Désactivé ({e})")
                self.use_llm = False

        # Dernier résultat (pour copier)
        self.last_result = ""

        # État
        self.is_processing = False

        print("🚀 Screen Tutor Assistant démarré")
        print(f"   OCR: OCRSpace API ({self.ocr_lang})")
        print(f"   Mode debug: {'✓ Activé' if self.debug_mode else '✗ Désactivé'}")
        print("\n📌 Raccourcis:")
        print("   = - Capturer l'écran et analyser")
        print("   ESC - Quitter l'application")
        print("\n✨ Les réponses s'afficheront en popup")
        print("En attente...\n")

    def show_notification(self, title: str, message: str, sound: bool = True):
        """Affiche une fenêtre popup macOS.
        
        Args:
            title: Titre de la popup
            message: Message de la popup
            sound: Non utilisé (pour compatibilité)
        """
        try:
            # Échapper les guillemets
            title = title.replace('"', '\\"').replace("'", "'")
            message = message.replace('"', '\\"').replace("'", "'")
            
            # Utiliser un dialog au lieu d'une notification
            script = f'display dialog "{message}" with title "{title}" buttons {{"OK"}} default button "OK"'
            
            # Exécuter en arrière-plan pour ne pas bloquer
            subprocess.Popen(
                ['osascript', '-e', script],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
                
        except Exception as e:
            print(f"⚠️  Erreur popup: {e}")

    def _extract_answers_summary(self, response: str) -> str:
        """Extrait un résumé des réponses pour la notification.
        
        Args:
            response: Réponse complète du LLM
            
        Returns:
            Résumé court pour notification
        """
        # Chercher les lignes avec "RÉPONSE:"
        lines = response.split('\n')
        answers = []
        
        for i, line in enumerate(lines):
            if '✅ RÉPONSE:' in line or 'RÉPONSE:' in line:
                # Extraire la réponse
                answer = line.split('RÉPONSE:')[-1].strip()
                answers.append(f"Q{len(answers)+1}: {answer}")
        
        if answers:
            return " | ".join(answers[:3])  # Max 3 réponses dans la notif
        else:
            return "Analyse terminée - Voir terminal"

    def process_screen_capture(self):
        """Pipeline: capture -> OCRSpace API -> (optionnel LLM) -> UI."""
        if self.is_processing:
            print("⚠️  Traitement déjà en cours, veuillez patienter...")
            return

        self.is_processing = True

        try:
            print("📸 Capture de l'écran...")
            
            # 1. Capture d'écran
            image = capture_screen(debug_mode=self.debug_save)
            if not image:
                print("❌ Échec de la capture d'écran")
                self.is_processing = False
                return

            # 2. OCR via OCRSpace API
            print("🔍 Extraction du texte via OCRSpace...")
            text, success = self.ocr_api.extract_text(image)

            if not success or not text:
                print("❌ Échec de l'extraction OCR")
                self.show_notification(
                    "Erreur OCR",
                    "Impossible d'extraire le texte. Vérifiez votre clé API."
                )
                self.is_processing = False
                return

            print(f"✓ Texte extrait: {len(text)} caractères")

            # 3. Analyse par LLM
            print("🤖 Analyse du QCM par l'IA...")
            if self.use_llm and self.llm_client:
                response = self.llm_client.analyze_qcm_text(text)
                if response:
                    # Extraire juste les réponses pour la notification
                    notification_text = self._extract_answers_summary(response)
                    
                    # Afficher notification
                    self.show_notification("🎯 Réponses QCM", notification_text)
                    
                    # Afficher aussi dans le terminal
                    print("\n" + "="*70)
                    print("🎯 RÉPONSES:")
                    print("="*70)
                    print(response)
                    print("="*70 + "\n")
                    
                    final_text = response
                    print("✓ Réponse affichée")
                else:
                    self.show_notification("⚠️ Erreur", "Impossible d'analyser le QCM")
                    final_text = "Impossible d'analyser le QCM"
                    print("❌ Erreur analyse LLM")
            else:
                self.show_notification(
                    "⚠️ Configuration",
                    "LLM non configuré. Activez USE_LLM dans .env"
                )
                final_text = text
                print("⚠️  LLM désactivé")
            
            # Sauvegarder le dernier résultat
            self.last_result = final_text

        except ValueError as e:
            # Erreur de clé API
            print(f"❌ {e}")
            print("\n⚠️  CONFIGURATION MANQUANTE")
            print("="*70)
            print(str(e))
            print("="*70 + "\n")
            self.is_processing = False
        except Exception as e:
            print(f"❌ Erreur: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
        finally:
            self.is_processing = False

    def copy_last_result(self):
        """Copie le dernier résultat dans le presse-papiers."""
        if self.last_result:
            try:
                pyperclip.copy(self.last_result)
                self.show_notification("✓ Copié", "Réponse copiée dans le presse-papiers")
                print("✓ Résultat copié dans le presse-papiers!")
            except Exception as e:
                self.show_notification("⚠️ Erreur", "Impossible de copier")
                print(f"⚠️  Impossible de copier: {e}")
        else:
            self.show_notification("⚠️ Info", "Aucun résultat. Appuyez sur P d'abord.")
            print("⚠️  Aucun résultat à copier. Faites d'abord une capture (P).")

    def on_copy_hotkey(self):
        """Gère l'appui sur la touche C."""
        self.copy_last_result()

    def _show_overlay(self, title: str, content: str):
        """Fonction supprimée - version terminal."""
        pass

    def _show_error(self, title: str, message: str):
        """Fonction supprimée - version terminal."""
        pass

    def on_hotkey_press(self):
        """Gère l'appui sur la touche =."""
        print("\n" + "="*50)
        print("⌨️  Hotkey '=' pressée - Début du traitement")
        print("="*50)
        
        # Lancer dans un thread pour ne pas bloquer keyboard
        thread = threading.Thread(target=self.process_screen_capture, daemon=True)
        thread.start()

    def on_press(self, key):
        """Callback pour les touches pressées."""
        try:
            # Vérifier quelle touche
            if hasattr(key, 'char'):
                if key.char == '=':
                    self.on_hotkey_press()
        except AttributeError:
            # Touche spéciale (ESC, etc.)
            if key == kb.Key.esc:
                self.quit()

    def run(self):
        """Lance l'application et écoute les hotkeys."""
        try:
            # Créer un listener pour les touches
            with kb.Listener(on_press=self.on_press) as listener:
                listener.join()

        except KeyboardInterrupt:
            print("\n⏹️  Interruption utilisateur")
            self.quit()
        except Exception as e:
            print(f"❌ Erreur fatale: {e}")
            if self.debug_mode:
                import traceback
                traceback.print_exc()
            sys.exit(1)

    def quit(self):
        """Quitte l'application proprement."""
        print("\n👋 Arrêt de l'application...")
        sys.exit(0)


def main():
    """Point d'entrée principal."""
    # Vérifier les dépendances critiques
    try:
        import pytesseract
        from PIL import Image
        import mss
        import requests
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("Exécutez: pip install -r requirements.txt")
        sys.exit(1)

    # Vérifier le fichier .env
    if not os.path.exists(".env"):
        print("⚠️  Fichier .env manquant!")
        print("Copiez .env.example vers .env")
        print("cp .env.example .env")
        sys.exit(1)

    # Charger les variables
    load_dotenv()
    
    # Vérifier la clé OCRSpace
    if not os.getenv("OCRSPACE_API_KEY"):
        print("❌ Clé API OCRSpace manquante dans .env")
        print("\n📝 Obtenez une clé API gratuite ici:")
        print("   https://ocr.space/ocrapi")
        print("\nPuis ajoutez-la dans .env:")
        print("   OCRSPACE_API_KEY=votre_clé_ici")
        sys.exit(1)

    # Lancer l'application
    app = ScreenTutorApp()
    app.run()


if __name__ == "__main__":
    main()
