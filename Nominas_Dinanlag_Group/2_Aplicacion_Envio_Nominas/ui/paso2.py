import tkinter as tk
from tkinter import ttk


class Paso2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(
            self, text="Paso 2: Verificación de Datos",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # --- Tabla de Verificación ---
        tree_frame = tk.Frame(self)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Página", "NIF", "Nombre", "Email", "Estado"),
            show="headings"
        )
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # --- Configuración de Columnas y Cabeceras ---
        headings = {
            "Página": 50, "NIF": 100, "Nombre": 200,
            "Email": 250, "Estado": 150
        }
        for col, width in headings.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # --- Estilos de Filas y Tags ---
        self.tree.tag_configure('ok', foreground='green')
        self.tree.tag_configure('error', foreground='red')
        self.tree.tag_configure('warning', foreground='orange')
        self.tree.tag_configure('oddrow', background='#FFFFFF')
        self.tree.tag_configure('evenrow', background='#F0F0F0')

        # --- Navegación ---
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Button(
            nav_frame, text="← Anterior",
            command=lambda: controller.mostrar_frame("Paso1")
        ).pack(side="left")
        tk.Button(
            nav_frame, text="Siguiente →",
            command=lambda: controller.mostrar_frame("Paso3")
        ).pack(side="right")

    def actualizar_tabla(self):
        self.tree.delete(*self.tree.get_children())
        for i, tarea in enumerate(self.controller.tareas_verificacion):
            row_style = 'evenrow' if i % 2 else 'oddrow'
            status = tarea["status"]
            
            status_tag = 'ok'
            if status.startswith("❌"):
                status_tag = 'error'
            elif status.startswith("⚠️"):
                status_tag = 'warning'
            
            self.tree.insert(
                "", "end",
                values=list(tarea.values()), tags=(row_style, status_tag))
