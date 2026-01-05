"""Interface utilisateur overlay avec tkinter."""

import tkinter as tk
from tkinter import scrolledtext, messagebox
from typing import Optional, Callable
import threading


class OverlayWindow:
    """Fenêtre overlay pour afficher les résultats."""

    def __init__(
        self,
        on_reveal_callback: Optional[Callable] = None,
        on_close_callback: Optional[Callable] = None
    ):
        """
        Initialise la fenêtre overlay.

        Args:
            on_reveal_callback: Fonction appelée lors du clic sur "Révéler"
            on_close_callback: Fonction appelée lors de la fermeture
        """
        self.on_reveal = on_reveal_callback
        self.on_close = on_close_callback
        self.window: Optional[tk.Tk] = None
        self.ocr_text_widget: Optional[scrolledtext.ScrolledText] = None
        self.explanation_widget: Optional[scrolledtext.ScrolledText] = None
        self.reveal_button: Optional[tk.Button] = None
        self.copy_button: Optional[tk.Button] = None
        self.is_revealed = False

    def create_window(self):
        """Crée et configure la fenêtre overlay."""
        self.window = tk.Tk()
        self.window.title("Screen Tutor Assistant")
        
        # Configuration de la fenêtre
        window_width = 700
        window_height = 600
        
        # Centrer la fenêtre
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Toujours au-dessus
        self.window.attributes("-topmost", True)
        
        # Configuration du protocole de fermeture
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Frame principal avec padding
        main_frame = tk.Frame(self.window, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section Texte OCR
        ocr_label = tk.Label(
            main_frame,
            text="📄 Texte OCR extrait:",
            font=("Arial", 11, "bold")
        )
        ocr_label.pack(anchor=tk.W, pady=(0, 5))

        self.ocr_text_widget = scrolledtext.ScrolledText(
            main_frame,
            height=8,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg="#f5f5f5",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.ocr_text_widget.pack(fill=tk.BOTH, expand=False, pady=(0, 15))
        self.ocr_text_widget.config(state=tk.DISABLED)

        # Section Explication
        explanation_label = tk.Label(
            main_frame,
            text="💡 Explication & Indice:",
            font=("Arial", 11, "bold")
        )
        explanation_label.pack(anchor=tk.W, pady=(0, 5))

        self.explanation_widget = scrolledtext.ScrolledText(
            main_frame,
            height=15,
            wrap=tk.WORD,
            font=("Arial", 10),
            bg="#ffffff",
            relief=tk.SOLID,
            borderwidth=1
        )
        self.explanation_widget.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.explanation_widget.config(state=tk.DISABLED)

        # Frame pour les boutons
        button_frame = tk.Frame(main_frame)
        button_frame.pack(fill=tk.X)

        # Bouton Révéler
        self.reveal_button = tk.Button(
            button_frame,
            text="🔓 Révéler la réponse",
            command=self._on_reveal_click,
            font=("Arial", 10, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.reveal_button.pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Copier
        self.copy_button = tk.Button(
            button_frame,
            text="📋 Copier",
            command=self._on_copy_click,
            font=("Arial", 10),
            bg="#2196F3",
            fg="white",
            activebackground="#0b7dda",
            cursor="hand2",
            padx=20,
            pady=8
        )
        self.copy_button.pack(side=tk.LEFT, padx=(0, 10))

        # Bouton Fermer
        close_button = tk.Button(
            button_frame,
            text="❌ Fermer",
            command=self._on_close,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            activebackground="#da190b",
            cursor="hand2",
            padx=20,
            pady=8
        )
        close_button.pack(side=tk.RIGHT)

    def set_ocr_text(self, text: str):
        """
        Affiche le texte OCR.

        Args:
            text: Texte OCR à afficher
        """
        if self.ocr_text_widget:
            self.ocr_text_widget.config(state=tk.NORMAL)
            self.ocr_text_widget.delete(1.0, tk.END)
            self.ocr_text_widget.insert(1.0, text)
            self.ocr_text_widget.config(state=tk.DISABLED)

    def set_explanation(self, text: str):
        """
        Affiche l'explication du tuteur.

        Args:
            text: Explication à afficher
        """
        if self.explanation_widget:
            self.explanation_widget.config(state=tk.NORMAL)
            self.explanation_widget.delete(1.0, tk.END)
            self.explanation_widget.insert(1.0, text)
            self.explanation_widget.config(state=tk.DISABLED)

    def append_explanation(self, text: str):
        """
        Ajoute du texte à l'explication existante.

        Args:
            text: Texte à ajouter
        """
        if self.explanation_widget:
            self.explanation_widget.config(state=tk.NORMAL)
            self.explanation_widget.insert(tk.END, "\n\n" + "="*50 + "\n\n")
            self.explanation_widget.insert(tk.END, text)
            self.explanation_widget.see(tk.END)
            self.explanation_widget.config(state=tk.DISABLED)

    def show_loading(self, message: str = "Chargement..."):
        """
        Affiche un message de chargement.

        Args:
            message: Message à afficher
        """
        if self.explanation_widget:
            self.explanation_widget.config(state=tk.NORMAL)
            self.explanation_widget.delete(1.0, tk.END)
            self.explanation_widget.insert(1.0, f"⏳ {message}")
            self.explanation_widget.config(state=tk.DISABLED)

    def _on_reveal_click(self):
        """Gère le clic sur le bouton Révéler."""
        if not self.is_revealed:
            self.is_revealed = True
            if self.reveal_button:
                self.reveal_button.config(state=tk.DISABLED, text="⏳ Chargement...")
            
            if self.on_reveal:
                # Exécuter dans un thread pour ne pas bloquer l'UI
                threading.Thread(target=self.on_reveal, daemon=True).start()

    def enable_reveal_button(self):
        """Active le bouton Révéler après le chargement."""
        if self.reveal_button:
            self.reveal_button.config(state=tk.NORMAL, text="✓ Réponse révélée")

    def _on_copy_click(self):
        """Copie le contenu dans le presse-papiers."""
        if self.explanation_widget:
            content = self.explanation_widget.get(1.0, tk.END)
            self.window.clipboard_clear()
            self.window.clipboard_append(content)
            messagebox.showinfo("Copié", "Contenu copié dans le presse-papiers!")

    def _on_close(self):
        """Gère la fermeture de la fenêtre."""
        if self.on_close:
            self.on_close()
        if self.window:
            self.window.destroy()
            self.window = None

    def show(self):
        """Affiche la fenêtre et lance la boucle principale."""
        if not self.window:
            self.create_window()
        self.window.mainloop()

    def close(self):
        """Ferme la fenêtre."""
        self._on_close()


def create_and_show_overlay(
    ocr_text: str,
    explanation: str,
    on_reveal: Optional[Callable] = None
) -> OverlayWindow:
    """
    Fonction utilitaire pour créer et afficher une overlay.

    Args:
        ocr_text: Texte OCR à afficher
        explanation: Explication initiale
        on_reveal: Callback pour le bouton Révéler

    Returns:
        Instance de OverlayWindow
    """
    overlay = OverlayWindow(on_reveal_callback=on_reveal)
    overlay.create_window()
    overlay.set_ocr_text(ocr_text)
    overlay.set_explanation(explanation)
    return overlay
