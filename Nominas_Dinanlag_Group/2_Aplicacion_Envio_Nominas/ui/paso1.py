import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import fitz  # PyMuPDF
from logic.file_handler import (
    leer_cabeceras_empleados, leer_archivo_empleados, analizar_archivos
)


class Paso1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        tk.Label(
            self, text="Paso 1: Selección de Archivos",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, pady=(0, 20), sticky="w")

        # --- Sección de PDF de Nóminas ---
        pdf_section_frame = ttk.LabelFrame(
            self, text=" 1. Archivo PDF de Nóminas "
        )
        pdf_section_frame.grid(row=1, column=0, sticky="new", pady=5)
        pdf_section_frame.grid_columnconfigure(0, weight=1)

        pdf_selector_frame = tk.Frame(pdf_section_frame, bg="#f0f0f0")
        pdf_selector_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
        pdf_selector_frame.grid_columnconfigure(1, weight=1)

        # Campo de texto y botón examinar estilo Windows
        self.pdf_path_entry = tk.Entry(pdf_selector_frame, font=("MS Sans Serif", 8), state="readonly")
        self.pdf_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=5)
        
        self.pdf_browse_btn = tk.Button(
            pdf_selector_frame, text="Examinar...",
            font=("MS Sans Serif", 8), width=12,
            command=self.seleccionar_pdf,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.pdf_browse_btn.grid(row=0, column=1, pady=5)
        
        # Información del archivo
        self.pdf_summary_label = tk.Label(
            pdf_selector_frame, text="Seleccione un archivo PDF con nóminas",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040", justify="left"
        )
        self.pdf_summary_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        pdf_selector_frame.grid_columnconfigure(0, weight=1)

        # --- Sección de Datos de Empleados ---
        employee_section_frame = ttk.LabelFrame(
            self, text=" 2. Archivo de Datos de Empleados "
        )
        employee_section_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        employee_section_frame.grid_columnconfigure(0, weight=1)
        employee_section_frame.grid_rowconfigure(2, weight=1)

        employee_selector_frame = tk.Frame(employee_section_frame, bg="#f0f0f0")
        employee_selector_frame.grid(
            row=0, column=0, sticky="ew", padx=10, pady=5
        )
        employee_selector_frame.grid_columnconfigure(0, weight=1)

        # Campo de texto y botón examinar estilo Windows
        self.empleados_path_entry = tk.Entry(employee_selector_frame, font=("MS Sans Serif", 8), state="readonly")
        self.empleados_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=5)
        
        self.empleados_browse_btn = tk.Button(
            employee_selector_frame, text="Examinar...",
            font=("MS Sans Serif", 8), width=12,
            command=self.seleccionar_empleados,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.empleados_browse_btn.grid(row=0, column=1, pady=5)
        
        # Información del archivo
        self.employee_summary_label = tk.Label(
            employee_selector_frame, text="Seleccione un archivo CSV o Excel con datos de empleados",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040", justify="left"
        )
        self.employee_summary_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(5, 0))
        
        employee_selector_frame.grid_columnconfigure(0, weight=1)

        # --- Frame para Vista Previa y Mapeo (inicialmente oculto) ---
        self.details_frame = ttk.Frame(employee_section_frame)
        self.details_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.details_frame.grid_columnconfigure(0, weight=1)

        # --- Vista Previa de Empleados ---
        preview_frame = ttk.LabelFrame(
            self.details_frame, text=" Vista Previa de Datos "
        )
        preview_frame.grid(row=0, column=0, sticky="ew", pady=(10, 5))
        preview_frame.grid_columnconfigure(0, weight=1)

        self.preview_tree = ttk.Treeview(preview_frame, height=3)
        self.preview_tree.grid(row=0, column=0, sticky="ew")

        # --- Mapeo de Columnas ---
        mapping_frame = ttk.LabelFrame(
            self.details_frame, text=" Asignación de Columnas "
        )
        mapping_frame.grid(row=1, column=0, sticky="ew", pady=5)
        mapping_frame.grid_columnconfigure(1, weight=1)

        labels = ["NIF:", "NOMBRE:", "EMAIL:"]
        variables = ["nif", "nombre", "email"]
        self.combos = {}

        for i, (label, var) in enumerate(zip(labels, variables)):
            tk.Label(mapping_frame, text=label).grid(
                row=i, column=0, padx=10, pady=5, sticky="w"
            )
            combo = ttk.Combobox(
                mapping_frame,
                textvariable=self.controller.mapa_columnas[var],
                state="readonly"
            )
            combo.grid(row=i, column=1, sticky="ew", padx=10)
            combo.bind("<<ComboboxSelected>>", self.verificar_estado)
            self.combos[var] = combo

        # --- Navegación ---
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=3, column=0, sticky="se", pady=20, padx=10)

        self.siguiente_btn = tk.Button(
            nav_frame, text="Siguiente →",
            command=self.ir_a_paso2, state="disabled"
        )
        self.siguiente_btn.pack()

        self.actualizar_visibilidad_detalles()

    def seleccionar_pdf(self):
        path = filedialog.askopenfilename(
            title="Seleccionar PDF Maestro",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=self.controller.last_dir
        )
        if path:
            self.controller.pdf_path.set(path)
            self.controller.last_dir = os.path.dirname(path)
            
            # Actualizar campo de texto
            self.pdf_path_entry.config(state="normal")
            self.pdf_path_entry.delete(0, tk.END)
            self.pdf_path_entry.insert(0, path)
            self.pdf_path_entry.config(state="readonly")
            
            self.actualizar_resumen_pdf()
            self.verificar_estado()

    def seleccionar_empleados(self):
        path = filedialog.askopenfilename(
            title="Seleccionar Archivo de Empleados",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Archivos CSV", "*.csv")
            ],
            initialdir=self.controller.last_dir
        )
        if path:
            self.controller.empleados_path.set(path)
            self.controller.last_dir = os.path.dirname(path)
            
            # Actualizar campo de texto
            self.empleados_path_entry.config(state="normal")
            self.empleados_path_entry.delete(0, tk.END)
            self.empleados_path_entry.insert(0, path)
            self.empleados_path_entry.config(state="readonly")
            
            self.actualizar_mapeo_columnas()
            self.actualizar_resumen_empleados()
            self.verificar_estado()
        self.actualizar_visibilidad_detalles()

    def actualizar_mapeo_columnas(self):
        path = self.controller.empleados_path.get()
        if path:
            self.controller.columnas_disponibles = \
                leer_cabeceras_empleados(path)
            for combo in self.combos.values():
                combo['values'] = self.controller.columnas_disponibles

    def actualizar_visibilidad_detalles(self):
        if self.controller.empleados_path.get():
            self.details_frame.grid()
        else:
            self.details_frame.grid_remove()

    def actualizar_resumen_pdf(self):
        pdf_path = self.controller.pdf_path.get()
        if pdf_path:
            try:
                doc = fitz.open(pdf_path)
                self.pdf_summary_label.config(
                    text=f"✓ Archivo válido: {doc.page_count} páginas encontradas",
                    fg="#008000"
                )
                doc.close()
            except Exception as e:
                self.pdf_summary_label.config(
                    text=f"✗ Error al leer el archivo: {str(e)[:50]}...",
                    fg="#800000"
                )

    def actualizar_resumen_empleados(self):
        empleados_path = self.controller.empleados_path.get()
        if empleados_path:
            try:
                df = leer_archivo_empleados(empleados_path)
                self.employee_summary_label.config(
                    text=f"✓ Archivo válido: {len(df)} empleados encontrados",
                    fg="#008000"
                )
                self.actualizar_vista_previa(df)
            except Exception as e:
                self.employee_summary_label.config(
                    text=f"✗ Error al leer el archivo: {str(e)[:50]}...",
                    fg="#800000"
                )

    def actualizar_vista_previa(self, df):
        self.preview_tree.delete(*self.preview_tree.get_children())
        
        columnas = list(df.columns)
        self.preview_tree["columns"] = columnas
        self.preview_tree.column("#0", width=0, stretch=tk.NO)
        self.preview_tree.heading("#0", text="")

        for col in columnas:
            self.preview_tree.heading(col, text=col, anchor=tk.W)
            self.preview_tree.column(
                col, anchor=tk.W, stretch=tk.YES, minwidth=100
            )

        for index, row in df.head(3).iterrows():
            self.preview_tree.insert("", "end", values=list(row))

    def verificar_estado(self, event=None):
        pdf_ok = bool(self.controller.pdf_path.get())
        empleados_ok = bool(self.controller.empleados_path.get())
        mapa_ok = all(
            var.get() for var in self.controller.mapa_columnas.values()
        )
        
        is_ready = pdf_ok and empleados_ok and mapa_ok
        self.siguiente_btn.config(state="normal" if is_ready else "disabled")

    def ir_a_paso2(self):
        mapa = {k: v.get() for k, v in self.controller.mapa_columnas.items()}
        res = analizar_archivos(
            self.controller.pdf_path.get(),
            self.controller.empleados_path.get(),
            mapa
        )
        
        if "error" in res:
            messagebox.showerror("Error de Análisis", res["error"])
            return
            
        self.controller.tareas_verificacion = res["tareas"]
        self.controller.frames["Paso2"].actualizar_tabla()
        self.controller.mostrar_frame("Paso2")
