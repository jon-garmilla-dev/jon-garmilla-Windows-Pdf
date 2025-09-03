import tkinter as tk
from tkinter import ttk, messagebox
from logic.settings import save_settings


class PasoAjustes(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        tk.Label(
            self, text="Ajustes de Correo Electrónico",
            font=("Helvetica", 16, "bold")
        ).pack(pady=(0, 20), anchor="w")

        settings_frame = ttk.LabelFrame(
            self, text=" Credenciales de Envío (Gmail) ")
        settings_frame.pack(fill="x", expand=False, pady=5)

        tk.Label(
            settings_frame, text="Email de Origen:"
        ).grid(row=0, column=0, sticky="w", pady=5, padx=10)
        self.email_entry = ttk.Entry(settings_frame, width=50)
        self.email_entry.grid(row=0, column=1, sticky="ew", padx=10)
        self.email_entry.insert(0, self.controller.config.get(
            'Email', 'email_origen', fallback=''))

        tk.Label(
            settings_frame, text="Contraseña de Aplicación:"
        ).grid(row=1, column=0, sticky="w", pady=5, padx=10)
        self.pass_entry = ttk.Entry(
            settings_frame, show="*", width=50)
        self.pass_entry.grid(row=1, column=1, sticky="ew", padx=10)
        self.pass_entry.insert(
            0, self.controller.config.get('Email', 'password', fallback=''))
        
        settings_frame.grid_columnconfigure(1, weight=1)

        # --- Botones ---
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20, anchor="e")
        
        tk.Button(
            btn_frame, text="Guardar Ajustes",
            command=self.save).pack(side="left", padx=10)
        tk.Button(
            btn_frame, text="Volver al Inicio",
            command=lambda: controller.mostrar_frame("Paso1")
        ).pack(side="right", padx=10)

    def save(self):
        self.controller.config.set(
            'Email', 'email_origen', self.email_entry.get())
        self.controller.config.set(
            'Email', 'password', self.pass_entry.get())
        save_settings(self.controller.config)
        messagebox.showinfo(
            "Guardado", "Configuración guardada correctamente.")
        self.controller.mostrar_frame("Paso1")
