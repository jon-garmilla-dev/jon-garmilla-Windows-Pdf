import tkinter as tk
from tkinter import ttk, messagebox, simpledialog


class Paso2(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.datos_corregidos = {}  # Para almacenar correcciones manuales
        
        # --- Título y Explicación ---
        titulo_frame = tk.Frame(self, bg="#f0f0f0")
        titulo_frame.pack(fill="x", pady=(0, 15))
        
        tk.Label(
            titulo_frame, text="Paso 2: Verificación de Datos",
            font=("MS Sans Serif", 14, "bold"), bg="#f0f0f0", fg="#000000"
        ).pack(anchor="w")
        
        tk.Label(
            titulo_frame, 
            text="Revise que los datos extraídos del PDF sean correctos antes del envío.",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040"
        ).pack(anchor="w", pady=(5, 0))

        # --- Panel de Estadísticas ---
        stats_frame = tk.LabelFrame(
            self, text=" Resumen de Verificación ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        stats_frame.pack(fill="x", pady=(0, 15))
        stats_frame.configure(bg="#f0f0f0")
        
        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg="#f0f0f0")
        stats_grid.pack(fill="x", padx=15, pady=10)
        
        # Contadores
        self.total_label = tk.Label(
            stats_grid, text="Total: 0",
            font=("MS Sans Serif", 9, "bold"), bg="#f0f0f0", fg="#000080"
        )
        self.total_label.pack(side="left", padx=(0, 20))
        
        self.ok_label = tk.Label(
            stats_grid, text="Listos para envío: 0",
            font=("MS Sans Serif", 9, "bold"), bg="#f0f0f0", fg="#008000"
        )
        self.ok_label.pack(side="left", padx=(0, 20))
        
        self.error_label = tk.Label(
            stats_grid, text="Con problemas: 0",
            font=("MS Sans Serif", 9, "bold"), bg="#f0f0f0", fg="#800000"
        )
        self.error_label.pack(side="left")

        # --- Explicación de Estados ---
        ayuda_frame = tk.LabelFrame(
            self, text=" Explicación de Estados ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        ayuda_frame.pack(fill="x", pady=(0, 15))
        ayuda_frame.configure(bg="#f0f0f0")
        
        ayuda_grid = tk.Frame(ayuda_frame, bg="#f0f0f0")
        ayuda_grid.pack(fill="x", padx=15, pady=8)
        
        # Indicadores de estado
        tk.Label(
            ayuda_grid, text="✅ OK:",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#008000"
        ).grid(row=0, column=0, sticky="w", padx=(0, 5))
        tk.Label(
            ayuda_grid, text="Datos completos y correctos, listo para envío",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=0, column=1, sticky="w")
        
        tk.Label(
            ayuda_grid, text="❌ ERROR:",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#800000"
        ).grid(row=1, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        tk.Label(
            ayuda_grid, text="Faltan datos o son incorrectos, requiere corrección",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=1, column=1, sticky="w", pady=(5, 0))
        
        tk.Label(
            ayuda_grid, text="⚠️ ADVERTENCIA:",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#B8860B"
        ).grid(row=2, column=0, sticky="w", padx=(0, 5), pady=(5, 0))
        tk.Label(
            ayuda_grid, text="Revise manualmente, puede necesitar corrección",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=2, column=1, sticky="w", pady=(5, 0))

        # --- Tabla de Verificación ---
        tabla_frame = tk.LabelFrame(
            self, text=" Datos Encontrados ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        tabla_frame.pack(fill="both", expand=True, pady=(0, 15))
        tabla_frame.configure(bg="#f0f0f0")
        
        # Crear frame para la tabla y scrollbar
        tree_container = tk.Frame(tabla_frame, bg="#f0f0f0")
        tree_container.pack(fill="both", expand=True, padx=8, pady=8)
        tree_container.grid_rowconfigure(0, weight=1)
        tree_container.grid_columnconfigure(0, weight=1)

        # Configurar estilo para la tabla
        style = ttk.Style()
        style.configure("Custom.Treeview", background="#ffffff", fieldbackground="#ffffff")
        style.configure("Custom.Treeview.Heading", background="#e0e0e0", font=("MS Sans Serif", 8, "bold"))

        self.tree = ttk.Treeview(
            tree_container,
            columns=("Página", "NIF", "Nombre", "Email", "Estado"),
            show="headings",
            style="Custom.Treeview",
            height=8
        )
        
        # Scrollbar
        vsb = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        # Configurar columnas con anchos apropiados
        headings = {
            "Página": 80, "NIF": 120, "Nombre": 180,
            "Email": 220, "Estado": 200
        }
        for col, width in headings.items():
            self.tree.heading(col, text=col, anchor="w")
            self.tree.column(col, width=width, anchor="w", stretch=True)

        # Estilos de filas con colores Windows
        self.tree.tag_configure('ok', background='#d4edda', foreground='#155724')
        self.tree.tag_configure('error', background='#f8d7da', foreground='#721c24')
        self.tree.tag_configure('warning', background='#fff3cd', foreground='#856404')
        self.tree.tag_configure('oddrow', background='#ffffff')
        self.tree.tag_configure('evenrow', background='#f8f9fa')

        # Doble click para editar
        self.tree.bind("<Double-1>", self.editar_fila)
        
        # --- Panel de Acciones ---
        acciones_frame = tk.LabelFrame(
            self, text=" Acciones de Corrección ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        acciones_frame.pack(fill="x", pady=(0, 15))
        acciones_frame.configure(bg="#f0f0f0")
        
        botones_frame = tk.Frame(acciones_frame, bg="#f0f0f0")
        botones_frame.pack(fill="x", padx=15, pady=10)
        
        # Botones de acción
        self.btn_editar = tk.Button(
            botones_frame, text="Corregir Seleccionado",
            font=("MS Sans Serif", 8), width=20, height=1,
            command=self.corregir_seleccionado,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_editar.pack(side="left", padx=(0, 10))
        
        self.btn_actualizar = tk.Button(
            botones_frame, text="Volver a Verificar",
            font=("MS Sans Serif", 8), width=20, height=1,
            command=self.reverificar_datos,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_actualizar.pack(side="left")
        
        # Ayuda
        self.btn_ayuda = tk.Button(
            botones_frame, text="¿Necesita Ayuda?",
            font=("MS Sans Serif", 8), width=15, height=1,
            command=self.mostrar_ayuda,
            relief="raised", bd=2, bg="#fff0e0"
        )
        self.btn_ayuda.pack(side="right")

        # --- Navegación estilo Windows ---
        nav_frame = tk.Frame(self, bg="#f0f0f0")
        nav_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # Separador estilo Windows
        separator = tk.Frame(nav_frame, height=1, bg="#c0c0c0", relief="sunken", bd=1)
        separator.pack(fill="x", pady=(0, 10))
        
        buttons_container = tk.Frame(nav_frame, bg="#f0f0f0")
        buttons_container.pack(side="right")
        
        self.btn_anterior = tk.Button(
            buttons_container, text="< Anterior",
            font=("MS Sans Serif", 8), width=12, height=2,
            command=lambda: self.controller.mostrar_frame("Paso1"),
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_anterior.pack(side="left", padx=(0, 8))
        
        self.btn_siguiente = tk.Button(
            buttons_container, text="Siguiente >",
            font=("MS Sans Serif", 8, "bold"), width=12, height=2,
            command=self.ir_a_paso3, state="disabled",
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_siguiente.pack(side="left")

    def actualizar_tabla(self):
        """Actualiza la tabla de verificación con los datos procesados."""
        # Limpiar tabla
        self.tree.delete(*self.tree.get_children())
        
        if not hasattr(self.controller, 'tareas_verificacion') or not self.controller.tareas_verificacion:
            messagebox.showinfo(
                "Sin Datos",
                "No hay datos para verificar.\n\n"
                "Asegúrese de haber seleccionado los archivos correctos en el Paso 1."
            )
            return
        
        # Contadores para estadísticas
        total = len(self.controller.tareas_verificacion)
        ok_count = 0
        error_count = 0
        warning_count = 0
        
        # Llenar tabla con datos
        for i, tarea in enumerate(self.controller.tareas_verificacion):
            row_style = 'evenrow' if i % 2 == 0 else 'oddrow'
            status = tarea["status"]
            
            # Determinar estilo y contar
            if status.startswith("✅"):
                status_tag = 'ok'
                ok_count += 1
            elif status.startswith("❌"):
                status_tag = 'error'
                error_count += 1
            elif status.startswith("⚠️"):
                status_tag = 'warning' 
                warning_count += 1
            else:
                status_tag = row_style
            
            # Aplicar correcciones manuales si existen
            pagina = tarea["pagina"]
            if pagina in self.datos_corregidos:
                correcciones = self.datos_corregidos[pagina]
                tarea_mostrada = tarea.copy()
                tarea_mostrada.update(correcciones)
                # Si se corrigió manualmente, marcar como OK
                if correcciones.get("status"):
                    tarea_mostrada["status"] = correcciones["status"]
                    status_tag = 'ok'
                    ok_count += 1
                    if status.startswith("❌"):
                        error_count -= 1
                    elif status.startswith("⚠️"):
                        warning_count -= 1
            else:
                tarea_mostrada = tarea
            
            # Insertar fila
            self.tree.insert(
                "", "end",
                values=list(tarea_mostrada.values()),
                tags=(row_style, status_tag)
            )
        
        # Actualizar estadísticas
        self.actualizar_estadisticas(total, ok_count, error_count + warning_count)
        
        # Habilitar botón siguiente si hay al menos uno OK
        if ok_count > 0:
            self.btn_siguiente.config(state="normal")
        else:
            self.btn_siguiente.config(state="disabled")

    def actualizar_estadisticas(self, total, ok_count, problem_count):
        """Actualiza las etiquetas de estadísticas."""
        self.total_label.config(text=f"Total: {total}")
        self.ok_label.config(text=f"Listos para envío: {ok_count}")
        self.error_label.config(text=f"Con problemas: {problem_count}")

    def editar_fila(self, event):
        """Permite editar una fila con doble click."""
        selected = self.tree.selection()
        if selected:
            self.corregir_seleccionado()

    def corregir_seleccionado(self):
        """Abre diálogo para corregir datos seleccionados."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo(
                "Selección Requerida",
                "Por favor seleccione una fila para corregir."
            )
            return
        
        item = selected[0]
        valores = self.tree.item(item, "values")
        
        if not valores:
            return
        
        pagina, nif, nombre, email, estado = valores
        
        # Crear ventana de corrección
        self.mostrar_dialogo_correccion(pagina, nif, nombre, email, estado)

    def mostrar_dialogo_correccion(self, pagina, nif, nombre, email, estado):
        """Muestra ventana para corregir datos manualmente."""
        ventana = tk.Toplevel(self)
        ventana.title(f"Corregir Datos - Página {pagina}")
        ventana.geometry("450x300")
        ventana.configure(bg="#f0f0f0")
        ventana.resizable(False, False)
        ventana.grab_set()  # Modal
        
        # Centrar ventana
        ventana.transient(self.controller)
        ventana.geometry("+%d+%d" % (
            self.controller.winfo_rootx() + 50,
            self.controller.winfo_rooty() + 50
        ))
        
        # Título
        tk.Label(
            ventana, text=f"Corrección Manual - Página {pagina}",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0"
        ).pack(pady=10)
        
        # Frame para campos
        campos_frame = tk.Frame(ventana, bg="#f0f0f0")
        campos_frame.pack(fill="x", padx=20, pady=10)
        
        # Variables para los campos
        var_nif = tk.StringVar(value=nif)
        var_nombre = tk.StringVar(value=nombre) 
        var_email = tk.StringVar(value=email)
        
        # Campos de entrada
        tk.Label(campos_frame, text="NIF:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=5)
        entry_nif = tk.Entry(campos_frame, textvariable=var_nif, width=40, font=("MS Sans Serif", 8))
        entry_nif.grid(row=0, column=1, pady=5)
        
        tk.Label(campos_frame, text="Nombre:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=5)
        entry_nombre = tk.Entry(campos_frame, textvariable=var_nombre, width=40, font=("MS Sans Serif", 8))
        entry_nombre.grid(row=1, column=1, pady=5)
        
        tk.Label(campos_frame, text="Email:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", pady=5)
        entry_email = tk.Entry(campos_frame, textvariable=var_email, width=40, font=("MS Sans Serif", 8))
        entry_email.grid(row=2, column=1, pady=5)
        
        # Información actual
        info_frame = tk.LabelFrame(ventana, text=" Estado Actual ", font=("MS Sans Serif", 8), bg="#f0f0f0")
        info_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        tk.Label(info_frame, text=estado, font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#800000").pack(pady=5)
        
        # Botones
        btn_frame = tk.Frame(ventana, bg="#f0f0f0")
        btn_frame.pack(pady=10)
        
        def guardar():
            # Validar campos
            if not var_nif.get().strip() or not var_nombre.get().strip() or not var_email.get().strip():
                messagebox.showerror("Error", "Todos los campos son obligatorios.")
                return
                
            # Validar email básico
            if "@" not in var_email.get() or "." not in var_email.get().split("@")[-1]:
                messagebox.showerror("Error", "El email no tiene un formato válido.")
                return
            
            # Guardar corrección
            self.datos_corregidos[int(pagina)] = {
                "nif": var_nif.get().strip(),
                "nombre": var_nombre.get().strip(), 
                "email": var_email.get().strip(),
                "status": "✅ OK (Corregido manualmente)"
            }
            
            ventana.destroy()
            self.actualizar_tabla()
            messagebox.showinfo("Éxito", "Datos corregidos correctamente.")
        
        def cancelar():
            ventana.destroy()
        
        tk.Button(btn_frame, text="Guardar", command=guardar, 
                 font=("MS Sans Serif", 8, "bold"), width=12, bg="#e0e0e0").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=cancelar,
                 font=("MS Sans Serif", 8), width=12, bg="#e0e0e0").pack(side="left", padx=5)

    def reverificar_datos(self):
        """Vuelve a ejecutar el análisis de archivos."""
        if messagebox.askyesno(
            "Reverificar Datos",
            "¿Desea volver a analizar los archivos?\n\n"
            "Esto eliminará todas las correcciones manuales realizadas."
        ):
            # Limpiar correcciones manuales
            self.datos_corregidos = {}
            
            # Re-ejecutar análisis
            from logic.file_handler import analizar_archivos
            
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
            self.actualizar_tabla()
            
            messagebox.showinfo("Completado", "Datos reverificados correctamente.")

    def mostrar_ayuda(self):
        """Muestra ayuda contextual para usuarios no técnicos."""
        ayuda_text = """
GUÍA RÁPIDA - VERIFICACIÓN DE DATOS

¿Qué estoy viendo?
• Esta tabla muestra los datos que se encontraron automáticamente en su archivo PDF
• Cada fila representa una nómina individual

Estados posibles:
✅ OK: Los datos están completos y listos para enviar
❌ ERROR: Faltan datos importantes, necesita corrección
⚠️ ADVERTENCIA: Revise manualmente los datos

¿Cómo corregir errores?
1. Haga doble clic en la fila con error
2. Complete o corrija los datos en la ventana que aparece
3. Haga clic en "Guardar"

¿Qué hacer si hay muchos errores?
• Revise que el archivo PDF sea correcto
• Verifique que el archivo de empleados tenga todos los datos
• Use "Volver a Verificar" después de corregir los archivos

¿Necesita más ayuda?
Contacte con soporte técnico o consulte el manual de usuario.
        """
        
        ventana_ayuda = tk.Toplevel(self)
        ventana_ayuda.title("Ayuda - Verificación de Datos")
        ventana_ayuda.geometry("500x400")
        ventana_ayuda.configure(bg="#f0f0f0")
        ventana_ayuda.grab_set()
        
        # Centrar
        ventana_ayuda.transient(self.controller)
        
        text_widget = tk.Text(
            ventana_ayuda, wrap=tk.WORD, font=("MS Sans Serif", 9),
            bg="#ffffff", relief="sunken", bd=2
        )
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget.insert("1.0", ayuda_text)
        text_widget.config(state="disabled")  # Solo lectura
        
        tk.Button(
            ventana_ayuda, text="Cerrar", 
            command=ventana_ayuda.destroy,
            font=("MS Sans Serif", 8), width=12, bg="#e0e0e0"
        ).pack(pady=10)

    def ir_a_paso3(self):
        """Navega al paso 3 aplicando las correcciones manuales."""
        # Aplicar correcciones a las tareas originales
        for i, tarea in enumerate(self.controller.tareas_verificacion):
            pagina = tarea["pagina"]
            if pagina in self.datos_corregidos:
                correcciones = self.datos_corregidos[pagina]
                # Actualizar la tarea original con las correcciones
                for key, value in correcciones.items():
                    if key != "status":  # No sobrescribir el estado automático
                        tarea[key] = value
                # Si fue corregido manualmente, marcarlo como OK
                if correcciones.get("status"):
                    tarea["status"] = "✅ OK"
        
        self.controller.mostrar_frame("Paso3")