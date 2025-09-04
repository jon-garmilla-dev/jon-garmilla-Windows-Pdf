import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import fitz  # PyMuPDF
from logic.file_handler import (
    leer_cabeceras_empleados, leer_archivo_empleados, analizar_archivos
)
from utils.sound_manager import play_error_sound


class Paso1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        tk.Label(
            self, text="Paso 1: Selección de Archivos",
            font=("MS Sans Serif", 14, "bold"), bg="#f0f0f0", fg="#000000"
        ).pack(pady=(0, 20), anchor="w")

        # --- Sección de PDF de Nóminas ---
        pdf_section_frame = tk.LabelFrame(
            self, text=" 1. Archivo PDF de Nóminas ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        pdf_section_frame.pack(fill="x", pady=(0, 10))
        pdf_section_frame.configure(bg="#f0f0f0")

        pdf_selector_frame = tk.Frame(pdf_section_frame, bg="#f0f0f0")
        pdf_selector_frame.pack(fill="x", padx=12, pady=8)
        pdf_selector_frame.grid_columnconfigure(0, weight=1)

        # Campo de texto y botón examinar estilo Windows
        self.pdf_path_entry = tk.Entry(pdf_selector_frame, font=("MS Sans Serif", 8), state="readonly")
        self.pdf_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.pdf_browse_btn = tk.Button(
            pdf_selector_frame, text="Examinar...",
            font=("MS Sans Serif", 8), width=12,
            command=self.seleccionar_pdf,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.pdf_browse_btn.grid(row=0, column=1)
        
        # Información del archivo
        self.pdf_summary_label = tk.Label(
            pdf_selector_frame,
            text="Seleccione un archivo PDF con nóminas",
            font=("MS Sans Serif", 8),
            bg="#f0f0f0",
            fg="#000080",
            justify="left")
        self.pdf_summary_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # --- Sección de Datos de Empleados ---
        employee_section_frame = tk.LabelFrame(
            self, text=" 2. Archivo de Datos de Empleados ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        employee_section_frame.pack(fill="both", expand=True)
        employee_section_frame.configure(bg="#f0f0f0")

        employee_selector_frame = tk.Frame(employee_section_frame, bg="#f0f0f0")
        employee_selector_frame.pack(fill="x", padx=12, pady=8)
        employee_selector_frame.grid_columnconfigure(0, weight=1)

        # Campo de texto y botón examinar estilo Windows
        self.empleados_path_entry = tk.Entry(employee_selector_frame, font=("MS Sans Serif", 8), state="readonly")
        self.empleados_path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        self.empleados_browse_btn = tk.Button(
            employee_selector_frame, text="Examinar...",
            font=("MS Sans Serif", 8), width=12,
            command=self.seleccionar_empleados,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.empleados_browse_btn.grid(row=0, column=1)
        
        # Información del archivo
        self.employee_summary_label = tk.Label(
            employee_selector_frame,
            text="Seleccione un archivo CSV o Excel con datos de empleados",
            font=("MS Sans Serif", 8),
            bg="#f0f0f0",
            fg="#000080",
            justify="left")
        self.employee_summary_label.grid(row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))

        # --- Frame para Vista Previa y Mapeo (inicialmente oculto) ---
        self.details_frame = tk.Frame(employee_section_frame, bg="#f0f0f0")
        self.details_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # --- Vista Previa de Empleados ---
        preview_frame = tk.LabelFrame(
            self.details_frame, text=" Vista Previa de Datos ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        preview_frame.pack(fill="both", expand=True, pady=(0, 8))
        preview_frame.configure(bg="#f0f0f0")

        # Crear frame contenedor con scrollbars
        preview_container = tk.Frame(preview_frame, bg="#f0f0f0")
        preview_container.pack(fill="both", expand=True, padx=8, pady=8)
        preview_container.grid_rowconfigure(0, weight=1)
        preview_container.grid_columnconfigure(0, weight=1)
        
        # Treeview con scroll horizontal y vertical
        self.preview_tree = ttk.Treeview(preview_container, height=4)
        self.preview_tree.grid(row=0, column=0, sticky="nsew")
        
        # Scrollbar vertical
        vsb_preview = ttk.Scrollbar(preview_container, orient="vertical", command=self.preview_tree.yview)
        vsb_preview.grid(row=0, column=1, sticky="ns")
        self.preview_tree.configure(yscrollcommand=vsb_preview.set)
        
        # Scrollbar horizontal
        hsb_preview = ttk.Scrollbar(preview_container, orient="horizontal", command=self.preview_tree.xview)
        hsb_preview.grid(row=1, column=0, sticky="ew")
        self.preview_tree.configure(xscrollcommand=hsb_preview.set)
        
        # Estilos de filas alternadas como en verificación
        self.preview_tree.tag_configure('oddrow', background='#FFFFFF')
        self.preview_tree.tag_configure('evenrow', background='#F0F0F0')

        # --- Mapeo de Columnas ---
        mapping_frame = tk.LabelFrame(
            self.details_frame, text=" Asignación de Columnas ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        mapping_frame.pack(fill="x")
        mapping_frame.configure(bg="#f0f0f0")

        # Grid interno para el mapeo
        mapping_grid = tk.Frame(mapping_frame, bg="#f0f0f0")
        mapping_grid.pack(fill="x", padx=12, pady=8)
        mapping_grid.grid_columnconfigure(1, weight=1)

        labels = ["NIF:", "NOMBRE:", "APELLIDOS:", "EMAIL:"]
        variables = ["nif", "nombre", "apellidos", "email"]
        self.combos = {}

        for i, (label, var) in enumerate(zip(labels, variables)):
            tk.Label(mapping_grid, text=label, 
                    font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000").grid(
                row=i, column=0, padx=(0, 10), pady=5, sticky="w"
            )
            combo = ttk.Combobox(
                mapping_grid,
                textvariable=self.controller.mapa_columnas[var],
                state="readonly",
                font=("MS Sans Serif", 8)
            )
            combo.grid(row=i, column=1, sticky="ew", pady=5)
            combo.bind("<<ComboboxSelected>>", self.verificar_estado)
            self.combos[var] = combo

        # --- Navegación ---
        nav_frame = tk.Frame(self, bg="#f0f0f0")
        nav_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # Separador estilo Windows
        separator = tk.Frame(nav_frame, height=1, bg="#c0c0c0", relief="sunken", bd=1)
        separator.pack(fill="x", pady=(0, 10))
        
        buttons_container = tk.Frame(nav_frame, bg="#f0f0f0")
        buttons_container.pack(side="right")

        self.siguiente_btn = tk.Button(
            buttons_container, text="Siguiente >",
            font=("MS Sans Serif", 8, "bold"), width=12, height=2,
            command=self.ir_a_paso2, state="disabled",
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.siguiente_btn.pack()

        self.actualizar_visibilidad_detalles()

    def seleccionar_pdf(self):
        inicial_dir = self.controller.config.get(
            'UltimosArchivos',
            'pdf_maestro',
            fallback=self.controller.last_dir)
        if inicial_dir and os.path.exists(os.path.dirname(inicial_dir)):
            inicial_dir = os.path.dirname(inicial_dir)
        else:
            inicial_dir = self.controller.last_dir
            
        path = self.controller.show_centered_filedialog(
            'openfilename',
            title="Seleccionar PDF Maestro",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=inicial_dir
        )
        if path:
            self.controller.pdf_path.set(path)
            self.controller.last_dir = os.path.dirname(path)
            
            # Guardar en configuración para próxima vez
            self.controller.config.set('UltimosArchivos', 'pdf_maestro', path)
            self.controller.guardar_configuracion()
            
            # Actualizar campo de texto
            self.pdf_path_entry.config(state="normal")
            self.pdf_path_entry.delete(0, tk.END)
            self.pdf_path_entry.insert(0, path)
            self.pdf_path_entry.config(state="readonly")
            
            self.actualizar_resumen_pdf()
            self.verificar_estado()

    def seleccionar_empleados(self):
        inicial_dir = self.controller.config.get(
            'UltimosArchivos',
            'excel_empleados',
            fallback=self.controller.last_dir)
        if inicial_dir and os.path.exists(os.path.dirname(inicial_dir)):
            inicial_dir = os.path.dirname(inicial_dir)
        else:
            inicial_dir = self.controller.last_dir
            
        path = self.controller.show_centered_filedialog(
            'openfilename',
            title="Seleccionar Archivo de Empleados",
            filetypes=[
                ("Archivos Excel", "*.xlsx *.xls"),
                ("Archivos CSV", "*.csv")
            ],
            initialdir=inicial_dir
        )
        if path:
            self.controller.empleados_path.set(path)
            self.controller.last_dir = os.path.dirname(path)
            
            # Guardar en configuración para próxima vez
            self.controller.config.set('UltimosArchivos', 'excel_empleados', path)
            self.controller.guardar_configuracion()
            
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
            
            # Auto-detección de columnas
            self.auto_detectar_columnas()

    def auto_detectar_columnas(self):
        """Auto-detecta las columnas basándose en nombres comunes"""
        if not self.controller.columnas_disponibles:
            return
            
        # Sistema de detección empresarial con niveles de confianza
        detecciones_candidatos = self._analizar_candidatos_columnas()
        
        # Seleccionar el mejor candidato para cada campo basado en confianza
        detecciones_finales = self._resolver_conflictos_deteccion(detecciones_candidatos)
        
        # Aplicar detecciones finales
        for field, info in detecciones_finales.items():
            if field in self.controller.mapa_columnas:
                self.controller.mapa_columnas[field].set(info['columna'])
                # Actualizar el combobox visualmente
                if field in self.combos:
                    self.combos[field].set(info['columna'])
                print(
                    f"AUTO-DETECTADO {field.upper()}: '{info['columna']}' "
                    f"(confianza: {info['confianza']}%)"
                )
    
    def _analizar_candidatos_columnas(self):
        """Analiza todas las columnas y genera candidatos con niveles de confianza"""
        candidatos = {
            'nif': [],
            'nombre': [], 
            'apellidos': [],
            'email': []
        }
        
        # Patrones con niveles de confianza (0-100)
        patrones_confianza = {
            'nif': [
                ('d.n.i.', 95),         # Formato español oficial
                ('dni', 90),            # Abreviatura común
                ('nif', 85),            # Identificador fiscal
                ('cedula', 70),         # Internacional
                ('documento', 60),      # Genérico
                ('identificacion', 55)   # Muy genérico
            ],
            'nombre': [
                ('nombre', 90),         # Directo
                ('name', 85),           # Inglés  
                ('empleado', 70),       # Contexto laboral
                ('persona', 65),        # Genérico
                ('trabajador', 60)      # Contexto específico
            ],
            'apellidos': [
                ('apellidos', 95),      # Plural, muy específico
                ('apellido', 90),       # Singular
                ('surname', 80),        # Inglés
                ('lastname', 75),       # Inglés alternativo
                ('familia', 60)         # Genérico
            ],
            'email': [
                ('dirección de correo electrónico', 98),
                ('direccion de correo electronico', 95),
                ('correo electrónico', 90),
                ('correo electronico', 88),
                ('email', 80),
                ('mail', 75),
                ('correo', 70),
            ],
        }
        
        # Analizar cada columna disponible
        for i, columna_original in enumerate(self.controller.columnas_disponibles):
            columna_lower = columna_original.lower()
            
            # Evaluar cada campo
            for campo, patrones in patrones_confianza.items():
                for patron, confianza_base in patrones:
                    if patron in columna_lower:
                        confianza_final = self._calcular_confianza_contextual(
                            columna_lower,
                            patron,
                            confianza_base,
                            campo)
                        
                        candidatos[campo].append({
                            'columna': columna_original,
                            'patron_detectado': patron,
                            'confianza': confianza_final,
                            'indice': i
                        })
        
        return candidatos
    
    def _calcular_confianza_contextual(self, columna_lower, patron, confianza_base, campo):
        """Ajusta la confianza basada en el contexto de la columna"""
        confianza = confianza_base
        
        # Penalizaciones por contextos negativos
        penalizaciones = {
            'nif': ['seguridad', 'social', 'afiliacion'],
            'nombre': ['apellido', 'surname', 'last'],
            'apellidos': [],  # Los apellidos no se penalizan fácilmente
            'email': ['telefono', 'phone', 'numero']
        }
        
        # Aplicar penalizaciones
        for palabra_negativa in penalizaciones.get(campo, []):
            if palabra_negativa in columna_lower:
                confianza -= 30  # Penalización significativa
        
        # Bonificaciones por contextos positivos  
        bonificaciones = {
            'nif': ['documento', 'identidad'],
            'nombre': ['empleado', 'trabajador'],
            'apellidos': ['familia'],
            'email': ['electronico', 'contacto']
        }
        
        for palabra_positiva in bonificaciones.get(campo, []):
            if palabra_positiva in columna_lower and palabra_positiva != patron:
                confianza += 5  # Pequeña bonificación
        
        # Asegurar que la confianza esté en rango válido
        return max(0, min(100, confianza))
    
    def _resolver_conflictos_deteccion(self, candidatos):
        """Resuelve conflictos eligiendo el candidato con mayor confianza."""
        detecciones_finales = {}
        columnas_usadas = set()

        campos_prioridad = ['nif', 'email', 'apellidos', 'nombre']

        for campo in campos_prioridad:
            lista_candidatos = candidatos[campo]
            if not lista_candidatos:
                continue

            lista_candidatos.sort(
                key=lambda x: (x['confianza'], len(x['patron_detectado'])),
                reverse=True)

            for candidato in lista_candidatos:
                if candidato['columna'] not in columnas_usadas:
                    if candidato['confianza'] >= 50:
                        detecciones_finales[campo] = candidato
                        columnas_usadas.add(candidato['columna'])
                        break

        for campo, info in detecciones_finales.items():
            print(
                f"Campo {campo.upper()}: "
                f"OK '{info['columna']}' ({info['confianza']}%)")

        return detecciones_finales

    def actualizar_visibilidad_detalles(self):
        if self.controller.empleados_path.get():
            self.details_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        else:
            self.details_frame.pack_forget()

    def actualizar_resumen_pdf(self):
        pdf_path = self.controller.pdf_path.get()
        if pdf_path:
            try:
                doc = fitz.open(pdf_path)
                self.pdf_summary_label.config(
                    text=f"OK - Archivo válido: {doc.page_count} páginas encontradas",
                    fg="#008000"
                )
                doc.close()
            except Exception as e:
                self.pdf_summary_label.config(
                    text=f"ERROR - Error al leer el archivo: {str(e)[:50]}...",
                    fg="#800000"
                )

    def actualizar_resumen_empleados(self):
        empleados_path = self.controller.empleados_path.get()
        if empleados_path:
            try:
                df = leer_archivo_empleados(empleados_path)
                self.employee_summary_label.config(
                    text=f"OK - Archivo válido: {len(df)} empleados encontrados",
                    fg="#008000")
                self.actualizar_vista_previa(df)
            except Exception as e:
                self.employee_summary_label.config(
                    text=f"ERROR - Error al leer el archivo: {str(e)[:50]}...",
                    fg="#800000")

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

        # Configurar estilo para la línea de separación
        self.preview_tree.tag_configure('separator', background='#E0E0E0', foreground='#666666')

        total_rows = len(df)
        row_count = 0

        # Mostrar los 3 primeros registros
        for i, (index, row) in enumerate(df.head(3).iterrows()):
            row_style = 'evenrow' if row_count % 2 else 'oddrow'
            self.preview_tree.insert("", "end", values=list(row), tags=(row_style,))
            row_count += 1

        # Si hay más de 4 registros, mostrar separador y último registro
        if total_rows > 4:
            # Crear fila separadora con "xxxx"
            separator_values = ["..." for _ in columnas]
            row_style = 'evenrow' if row_count % 2 else 'oddrow'
            self.preview_tree.insert("", "end", values=separator_values, tags=('separator',))
            row_count += 1
            
            # Mostrar el último registro
            last_row = df.tail(1).iloc[0]
            row_style = 'evenrow' if row_count % 2 else 'oddrow'
            self.preview_tree.insert("", "end", values=list(last_row), tags=(row_style,))
        elif total_rows == 4:
            # Si hay exactamente 4, mostrar el 4to sin separador
            fourth_row = df.iloc[3]
            row_style = 'evenrow' if row_count % 2 else 'oddrow'
            self.preview_tree.insert("", "end", values=list(fourth_row), tags=(row_style,))

    def verificar_estado(self, event=None):
        pdf_ok = bool(self.controller.pdf_path.get())
        empleados_ok = bool(self.controller.empleados_path.get())
        mapa_ok = all(
            var.get() for var in self.controller.mapa_columnas.values()
        )
        
        is_ready = pdf_ok and empleados_ok and mapa_ok
        self.siguiente_btn.config(state="normal" if is_ready else "disabled")

    def ir_a_paso2(self):
        print("[DEBUG] Iniciando transición a Paso 2...")
        mapa = {k: v.get() for k, v in self.controller.mapa_columnas.items()}
        print(f"[DEBUG] Mapa de columnas: {mapa}")
        print(f"[DEBUG] PDF: {self.controller.pdf_path.get()}")
        print(f"[DEBUG] Empleados: {self.controller.empleados_path.get()}")
        
        res = analizar_archivos(
            self.controller.pdf_path.get(),
            self.controller.empleados_path.get(),
            mapa
        )
        
        print(f"[DEBUG] Resultado análisis: {type(res)} con keys: {list(res.keys()) if isinstance(res, dict) else 'No dict'}")
        
        if "error" in res:
            play_error_sound()
            print(f"[DEBUG] Error en análisis: {res['error']}")
            self.controller.show_centered_messagebox("error", "Error de Análisis", res["error"])
            return
            
        self.controller.tareas_verificacion = res["tareas"]
        print(f"[DEBUG] Tareas creadas: {len(self.controller.tareas_verificacion) if self.controller.tareas_verificacion else 0}")
        
        self.controller.frames["Paso2"].actualizar_tabla()
        self.controller.ir_a_paso_siguiente("Paso2")
