import tkinter as tk
import os
from logic.settings import load_settings
from ui.paso1 import Paso1
from ui.paso2 import Paso2
from ui.paso3 import Paso3
from ui.paso_ajustes import PasoAjustes


class AsistenteNominas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asistente de Envío de Nóminas v2.0")
        self.geometry("1100x700")
        self.minsize(900, 600)
        
        self.config = load_settings()

        # Variables de estado compartidas
        self.pdf_path = tk.StringVar()
        self.empleados_path = tk.StringVar()
        self.last_dir = os.path.expanduser("~")
        self.columnas_disponibles = []
        self.mapa_columnas = {
            "nif": tk.StringVar(),
            "nombre": tk.StringVar(),
            "email": tk.StringVar()
        }
        self.tareas_verificacion = []

        self._crear_widgets()
        self.mostrar_frame("Paso1")

    def _crear_widgets(self):
        # Contenedor principal
        main_frame = tk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Panel lateral
        panel_lateral = tk.Frame(main_frame, bg="#e1e1e1", width=200)
        panel_lateral.pack(side="left", fill="y")

        tk.Label(
            panel_lateral, text="Proceso",
            font=("Helvetica", 14, "bold"), bg="#e1e1e1"
        ).pack(pady=10, padx=10)
        self.pasos_labels = {
            "Paso1": tk.Label(
                panel_lateral, text="1. Archivos", bg="#e1e1e1",
                anchor="w", font=("Helvetica", 11)),
            "Paso2": tk.Label(
                panel_lateral, text="2. Verificación", bg="#e1e1e1",
                anchor="w", font=("Helvetica", 11)),
            "Paso3": tk.Label(
                panel_lateral, text="3. Envío", bg="#e1e1e1",
                anchor="w", font=("Helvetica", 11)),
            "PasoAjustes": tk.Label(
                panel_lateral, text="⚙️ Ajustes", bg="#e1e1e1",
                anchor="w", font=("Helvetica", 11))
        }
        
        # Layout de los pasos y el botón de ajustes
        for name, label in self.pasos_labels.items():
            if name == "PasoAjustes":
                label.pack(fill="x", padx=20, pady=10, side=tk.BOTTOM)
            else:
                label.pack(fill="x", padx=20, pady=5, side=tk.TOP)
            
            label.bind(
                "<Button-1>",
                lambda e, page_name=name: self.mostrar_frame(page_name)
            )
            label.bind("<Enter>", lambda e: e.widget.config(cursor="hand2"))
            label.bind("<Leave>", lambda e: e.widget.config(cursor=""))

        # Contenedor para los pasos (frames)
        self.container = tk.Frame(main_frame)
        self.container.pack(
            side="right", fill="both", expand=True, padx=10, pady=10)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Paso1, Paso2, Paso3, PasoAjustes):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def mostrar_frame(self, page_name):
        """Muestra un frame y resalta el paso actual."""
        if page_name == "Paso3":
            self.event_generate("<<ShowPaso3>>")

        for name, label in self.pasos_labels.items():
            is_active = (name == page_name)
            font_weight = "bold" if is_active else "normal"
            bg_color = "#cce5ff" if is_active else "#e1e1e1"
            label.config(font=("Helvetica", 11, font_weight), bg=bg_color)
        
        frame = self.frames[page_name]
        frame.tkraise()

    def abrir_ajustes(self):
        self.mostrar_frame("PasoAjustes")
