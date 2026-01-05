"""Module de capture d'écran avec mss."""

import os
from typing import Optional
from PIL import Image
import mss


class ScreenCapture:
    """Gestionnaire de capture d'écran."""

    def __init__(self, debug_mode: bool = False, debug_save_path: Optional[str] = None):
        """
        Initialise le gestionnaire de capture.

        Args:
            debug_mode: Active le mode debug
            debug_save_path: Chemin pour sauvegarder les captures en mode debug
        """
        self.debug_mode = debug_mode
        self.debug_save_path = debug_save_path
        if debug_mode and debug_save_path:
            os.makedirs(debug_save_path, exist_ok=True)

    def capture_fullscreen(self) -> Optional[Image.Image]:
        """
        Capture l'écran complet.

        Returns:
            Image PIL de la capture, ou None en cas d'erreur

        Raises:
            Exception: En cas d'erreur de capture
        """
        try:
            with mss.mss() as sct:
                # Capture le premier moniteur (ou moniteur principal)
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)

                # Convertir en PIL Image
                img = Image.frombytes(
                    "RGB",
                    screenshot.size,
                    screenshot.bgra,
                    "raw",
                    "BGRX"
                )

                # Sauvegarder en mode debug
                if self.debug_mode and self.debug_save_path:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    debug_path = os.path.join(
                        self.debug_save_path,
                        f"capture_{timestamp}.png"
                    )
                    img.save(debug_path)
                    print(f"[DEBUG] Capture sauvegardée: {debug_path}")

                return img

        except Exception as e:
            print(f"Erreur lors de la capture d'écran: {e}")
            raise


def capture_screen(debug_mode: bool = False) -> Optional[Image.Image]:
    """
    Fonction utilitaire pour capturer l'écran.

    Args:
        debug_mode: Active le mode debug

    Returns:
        Image PIL de la capture
    """
    debug_path = "debug_screenshots" if debug_mode else None
    capturer = ScreenCapture(debug_mode, debug_path)
    return capturer.capture_fullscreen()
