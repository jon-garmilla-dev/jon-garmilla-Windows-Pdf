import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import fitz  # PyMuPDF
import io
import os
import sys
import subprocess
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
    print("[DEBUG] PIL cargado correctamente")
except ImportError as e:
    PIL_AVAILABLE = False
    print(f"[DEBUG] PIL no disponible: {e}")
except Exception as e:
    PIL_AVAILABLE = False
    print(f"[DEBUG] Error cargando PIL: {e}")


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
        
        # Botón para ver PDF completo
        self.btn_ver_pdf = tk.Button(
            botones_frame, text="Ver PDF Completo",
            font=("MS Sans Serif", 8), width=18, height=1,
            command=self.abrir_pdf_completo,
            relief="raised", bd=2, bg="#e8f4fd"
        )
        self.btn_ver_pdf.pack(side="right", padx=(0, 10))
        
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
            pagina = tarea["pagina"]
            
            # Verificar si hay corrección manual primero
            if pagina in self.datos_corregidos:
                correcciones = self.datos_corregidos[pagina]
                tarea_mostrada = tarea.copy()
                tarea_mostrada.update(correcciones)
                # Usar estado corregido
                status = correcciones.get("status", tarea["status"])
                tarea_mostrada["status"] = status
            else:
                tarea_mostrada = tarea
                status = tarea["status"]
            
            # Determinar estilo y contar (solo UNA vez por tarea)
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

    def crear_preview_pdf(self, pagina_num):
        """Crea una imagen preview de la página PDF especificada."""
        if not PIL_AVAILABLE:
            print("[DEBUG] PIL no disponible, saltando preview")
            return None
            
        try:
            pdf_path = self.controller.pdf_path.get()
            if not pdf_path:
                print("[DEBUG] No hay ruta PDF para preview")
                return None
                
            print(f"[DEBUG] Creando preview de página {pagina_num}")
            
            doc = fitz.open(pdf_path)
            page = doc.load_page(pagina_num - 1)  # pagina_num es 1-indexed
            
            # Renderizar página a imagen
            mat = fitz.Matrix(2.5, 2.5)  # escala 2.5x para mejor legibilidad
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("ppm")
            
            print(f"[DEBUG] Imagen generada, tamaño: {len(img_data)} bytes")
            
            # Convertir a PIL Image
            pil_image = Image.open(io.BytesIO(img_data))
            
            # Redimensionar para que quepa en la ventana (max 600px ancho)
            width, height = pil_image.size
            print(f"[DEBUG] Tamaño original: {width}x{height}")
            
            if width > 600:
                ratio = 600 / width
                new_width = 600
                new_height = int(height * ratio)
                pil_image = pil_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                print(f"[DEBUG] Redimensionado a: {new_width}x{new_height}")
            
            # Convertir a PhotoImage para tkinter
            photo = ImageTk.PhotoImage(pil_image)
            print("[DEBUG] PhotoImage creado exitosamente")
            
            doc.close()
            return photo
            
        except Exception as e:
            print(f"[DEBUG] Error creando preview: {type(e).__name__}: {e}")
            import traceback
            print(f"[DEBUG] Traceback: {traceback.format_exc()}")
            return None

    def mostrar_dialogo_correccion(self, pagina, nif, nombre, email, estado):
        """Muestra ventana para corregir datos manualmente."""
        ventana = tk.Toplevel(self)
        ventana.title(f"Corregir Datos - Página {pagina}")
        
        # Ajustar tamaño si hay preview
        if PIL_AVAILABLE:
            ventana.geometry("1100x650")
        else:
            ventana.geometry("500x350")
        
        ventana.configure(bg="#f0f0f0")
        ventana.resizable(True, True)  # Permitir redimensionar para ver PDF
        
        # Centrar ventana
        ventana.transient(self.controller)
        ventana.geometry("+%d+%d" % (
            self.controller.winfo_rootx() + 50,
            self.controller.winfo_rooty() + 50
        ))
        
        # Esperar a que la ventana esté completamente cargada antes del grab
        ventana.update_idletasks()
        try:
            ventana.grab_set()  # Modal
        except tk.TclError:
            print("[DEBUG] No se pudo establecer grab modal, continuando sin él")
        
        # Título
        tk.Label(
            ventana, text=f"Corrección Manual - Página {pagina}",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0"
        ).pack(pady=10)
        
        # Contenedor principal con dos columnas si hay preview
        main_container = tk.Frame(ventana, bg="#f0f0f0")
        main_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Variables para los campos
        var_nif = tk.StringVar(value=nif)
        var_nombre = tk.StringVar(value=nombre) 
        var_email = tk.StringVar(value=email)
        
        # Crear preview si está disponible
        preview_photo = None
        if PIL_AVAILABLE:
            preview_photo = self.crear_preview_pdf(int(pagina))
            
        if preview_photo:
            # Layout con dos columnas: preview + campos
            
            # Columna izquierda - Preview del PDF
            preview_frame = tk.LabelFrame(
                main_container, text=" Vista Previa del PDF ",
                font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
            )
            preview_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
            
            # Canvas con scrollbar para el PDF
            preview_canvas = tk.Canvas(
                preview_frame, bg="#ffffff", relief="sunken", bd=2,
                width=650, height=500
            )
            preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=preview_canvas.yview)
            preview_scrollbar.pack(side="right", fill="y")
            preview_canvas.configure(yscrollcommand=preview_scrollbar.set)
            preview_canvas.pack(side="left", fill="both", expand=True, padx=5, pady=5)
            
            # Mostrar imagen en canvas
            preview_canvas.create_image(10, 10, anchor="nw", image=preview_photo)
            preview_canvas.configure(scrollregion=preview_canvas.bbox("all"))
            
            # Mantener referencia a la imagen
            ventana.preview_photo = preview_photo
            
            # Columna derecha - Campos de edición
            campos_container = tk.Frame(main_container, bg="#f0f0f0", width=400)
            campos_container.pack(side="right", fill="y", anchor="n")
            campos_container.pack_propagate(False)  # Mantener ancho fijo
        else:
            # Layout simple sin preview
            campos_container = main_container
        
        # Frame para campos de edición
        campos_frame = tk.LabelFrame(
            campos_container, text=" Datos a Corregir ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        campos_frame.pack(fill="x", pady=(0, 10))
        
        campos_grid = tk.Frame(campos_frame, bg="#f0f0f0")
        campos_grid.pack(fill="x", padx=10, pady=10)
        
        # Campos de entrada
        tk.Label(campos_grid, text="NIF:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=5, padx=(0, 5))
        entry_nif = tk.Entry(campos_grid, textvariable=var_nif, width=30, font=("MS Sans Serif", 8))
        entry_nif.grid(row=0, column=1, sticky="ew", pady=5)
        
        tk.Label(campos_grid, text="Nombre:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=5, padx=(0, 5))
        entry_nombre = tk.Entry(campos_grid, textvariable=var_nombre, width=30, font=("MS Sans Serif", 8))
        entry_nombre.grid(row=1, column=1, sticky="ew", pady=5)
        
        tk.Label(campos_grid, text="Email:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=2, column=0, sticky="w", pady=5, padx=(0, 5))
        entry_email = tk.Entry(campos_grid, textvariable=var_email, width=30, font=("MS Sans Serif", 8))
        entry_email.grid(row=2, column=1, sticky="ew", pady=5)
        
        campos_grid.grid_columnconfigure(1, weight=1)
        
        # Información del estado actual
        info_frame = tk.LabelFrame(
            campos_container, text=" Estado Actual ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        info_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            info_frame, text=estado, 
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#800000",
            wraplength=300, justify="left"
        ).pack(padx=10, pady=8)
        
        # Tips de ayuda
        tips_frame = tk.LabelFrame(
            campos_container, text=" Ayuda ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        tips_frame.pack(fill="x", pady=(0, 10))
        
        tips_text = (
            "• Revise la nómina en la vista previa\n"
            "• Corrija los datos incorrectos\n" 
            "• Todos los campos son obligatorios"
        )
        if not PIL_AVAILABLE:
            tips_text = (
                "• Corrija los datos incorrectos\n"
                "• Todos los campos son obligatorios\n"
                "• Para ver PDFs instale: pip install Pillow"
            )
        
        tk.Label(
            tips_frame, text=tips_text,
            font=("MS Sans Serif", 7), bg="#f0f0f0", fg="#404040",
            justify="left"
        ).pack(padx=10, pady=5)
        
        # Botones
        btn_frame = tk.Frame(campos_container if preview_photo else ventana, bg="#f0f0f0")
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
        
        def ver_pdf_completo():
            """Abre el PDF en una ventana más grande."""
            # Reutilizar el método principal con mejor manejo de errores
            self.abrir_pdf_completo()
        
        # Botones principales
        tk.Button(btn_frame, text="Guardar", command=guardar, 
                 font=("MS Sans Serif", 8, "bold"), width=12, bg="#e0e0e0").pack(side="left", padx=5)
        tk.Button(btn_frame, text="Cancelar", command=cancelar,
                 font=("MS Sans Serif", 8), width=12, bg="#e0e0e0").pack(side="left", padx=5)
        
        # Botón para abrir PDF completo
        if preview_photo:
            tk.Button(btn_frame, text="Ver PDF Completo", command=ver_pdf_completo,
                     font=("MS Sans Serif", 7), width=15, bg="#fff8e0").pack(side="right", padx=5)

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

    def abrir_pdf_completo(self):
        """Abre el PDF maestro con el visualizador del sistema."""
        pdf_path = self.controller.pdf_path.get()
        
        if not pdf_path:
            messagebox.showwarning(
                "Sin PDF",
                "No hay ningún archivo PDF cargado para mostrar."
            )
            return
        
        # Verificar que el archivo existe
        if not os.path.exists(pdf_path):
            messagebox.showerror(
                "Archivo no encontrado",
                f"El archivo PDF no existe:\n{pdf_path}\n\n"
                "Verifique que el archivo no se haya movido o eliminado."
            )
            return
        
        # Información de diagnóstico para debugging
        print(f"[DEBUG] Intentando abrir PDF: {pdf_path}")
        print(f"[DEBUG] Archivo existe: {os.path.exists(pdf_path)}")
        print(f"[DEBUG] Plataforma: {sys.platform}")
        
        # Mostrar mensaje de que se está abriendo (más discreto)
        # messagebox.showinfo(
        #     "Abriendo PDF", 
        #     f"Abriendo el archivo PDF...\n\n{os.path.basename(pdf_path)}\n\n"
        #     "Si no se abre automáticamente, verifique que tenga un visor de PDF instalado."
        # )
        
        try:
            if sys.platform == "win32":
                # En Windows, intentar varios métodos
                try:
                    # Método 1: startfile (más compatible)
                    os.startfile(pdf_path)
                except OSError as e:
                    # Método 2: subprocess con cmd
                    subprocess.run(['cmd', '/c', 'start', '', pdf_path], check=True)
                    
            elif sys.platform == "darwin":
                # macOS
                result = subprocess.run(["open", pdf_path], capture_output=True, text=True)
                if result.returncode != 0:
                    raise subprocess.CalledProcessError(result.returncode, "open", result.stderr)
                    
            else:
                # Linux - intentar múltiples métodos
                print("[DEBUG] Intentando abrir PDF en Linux")
                success = False
                
                # Método 1: xdg-open (más común)
                try:
                    result = subprocess.run(
                        ["xdg-open", pdf_path], 
                        capture_output=True, 
                        text=True,
                        timeout=5,
                        shell=False  # Evitar problemas con shell
                    )
                    if result.returncode == 0:
                        success = True
                        print("[DEBUG] xdg-open exitoso")
                    else:
                        print(f"[DEBUG] xdg-open falló: {result.stderr}")
                except Exception as e:
                    print(f"[DEBUG] xdg-open excepción: {e}")
                
                # Método 2: Detectar visor de PDF específico
                if not success:
                    viewers = ['evince', 'okular', 'zathura', 'mupdf', 'firefox']
                    for viewer in viewers:
                        try:
                            # Verificar si el viewer existe
                            subprocess.run(['which', viewer], capture_output=True, check=True)
                            # Si existe, intentar abrir
                            result = subprocess.run(
                                [viewer, pdf_path], 
                                capture_output=True, 
                                text=True,
                                timeout=5
                            )
                            success = True
                            print(f"[DEBUG] {viewer} exitoso")
                            break
                        except Exception as e:
                            print(f"[DEBUG] {viewer} no disponible: {e}")
                            continue
                
                if not success:
                    raise subprocess.CalledProcessError(1, "pdf viewers", "No se encontró visor de PDF")
                
        except subprocess.CalledProcessError as e:
            messagebox.showerror(
                "Error al abrir PDF",
                f"No se pudo abrir el archivo PDF:\n{e}\n\n"
                f"Posibles soluciones:\n"
                f"• Instale un visor de PDF (Adobe Reader, SumatraPDF, etc.)\n"
                f"• Abra manualmente el archivo en:\n{pdf_path}"
            )
        except FileNotFoundError:
            messagebox.showerror(
                "Visor PDF no encontrado",
                f"No se encontró un visor de PDF en su sistema.\n\n"
                f"Instale un programa para ver PDFs o abra manualmente:\n{pdf_path}"
            )
        except Exception as e:
            # Mostrar diálogo con opciones adicionales
            self.mostrar_dialogo_error_pdf(pdf_path, e)

    def mostrar_dialogo_error_pdf(self, pdf_path, error):
        """Muestra diálogo de error con opciones para el usuario."""
        ventana_error = tk.Toplevel(self)
        ventana_error.title("Error al abrir PDF")
        ventana_error.geometry("500x350")
        ventana_error.configure(bg="#f0f0f0")
        ventana_error.resizable(False, False)
        
        # Centrar ventana
        ventana_error.transient(self.controller)
        ventana_error.geometry("+%d+%d" % (
            self.controller.winfo_rootx() + 100,
            self.controller.winfo_rooty() + 100
        ))
        
        # Esperar a que la ventana esté lista antes del grab
        ventana_error.update_idletasks()
        try:
            ventana_error.grab_set()
        except tk.TclError:
            print("[DEBUG] No se pudo establecer grab modal en diálogo error")
        
        # Título y explicación
        tk.Label(
            ventana_error, text="⚠️ No se pudo abrir el PDF",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0", fg="#800000"
        ).pack(pady=10)
        
        # Información del error
        error_frame = tk.LabelFrame(
            ventana_error, text=" Detalles del Error ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        error_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            error_frame, text=f"Error: {type(error).__name__}",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#800000"
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(
            error_frame, text=f"Detalle: {str(error)[:100]}{'...' if len(str(error)) > 100 else ''}",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040",
            wraplength=450
        ).pack(anchor="w", padx=10, pady=(0, 10))
        
        # Información del archivo
        archivo_frame = tk.LabelFrame(
            ventana_error, text=" Archivo PDF ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        archivo_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(
            archivo_frame, text=f"Archivo: {os.path.basename(pdf_path)}",
            font=("MS Sans Serif", 8), bg="#f0f0f0"
        ).pack(anchor="w", padx=10, pady=5)
        
        # Frame para la ruta con scrollbar
        ruta_frame = tk.Frame(archivo_frame, bg="#f0f0f0")
        ruta_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ruta_entry = tk.Entry(
            ruta_frame, font=("MS Sans Serif", 7), 
            bg="#ffffff", relief="sunken", bd=1
        )
        ruta_entry.pack(fill="x")
        ruta_entry.insert(0, pdf_path)
        ruta_entry.config(state="readonly")
        
        # Posibles soluciones
        soluciones_frame = tk.LabelFrame(
            ventana_error, text=" Posibles Soluciones ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0"
        )
        soluciones_frame.pack(fill="x", padx=20, pady=10)
        
        soluciones_text = (
            "• Instale un visor de PDF (Adobe Reader, SumatraPDF, etc.)\n"
            "• Verifique que el archivo no esté dañado\n"
            "• Copie la ruta y abra el archivo manualmente\n"
            "• Reinicie la aplicación si persiste el problema"
        )
        
        tk.Label(
            soluciones_frame, text=soluciones_text,
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000080",
            justify="left"
        ).pack(anchor="w", padx=10, pady=8)
        
        # Botones de acción
        btn_frame = tk.Frame(ventana_error, bg="#f0f0f0")
        btn_frame.pack(pady=15)
        
        def copiar_ruta():
            """Copia la ruta del archivo al clipboard."""
            try:
                ventana_error.clipboard_clear()
                ventana_error.clipboard_append(pdf_path)
                ventana_error.update()  # Necesario para que funcione el clipboard
                messagebox.showinfo("Copiado", f"Ruta copiada al portapapeles:\n\n{pdf_path}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo copiar al portapapeles:\n{e}")
        
        def abrir_carpeta():
            """Abre la carpeta que contiene el PDF."""
            try:
                carpeta = os.path.dirname(pdf_path)
                
                if sys.platform == "win32":
                    subprocess.run(['explorer', carpeta], shell=False)
                elif sys.platform == "darwin":
                    subprocess.run(["open", carpeta], shell=False)
                else:
                    # Linux - evitar problemas con shell
                    subprocess.run(["xdg-open", carpeta], shell=False, timeout=5)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{e}")
        
        def cerrar():
            ventana_error.destroy()
        
        # Botones
        tk.Button(
            btn_frame, text="Copiar Ruta", command=copiar_ruta,
            font=("MS Sans Serif", 8), width=12, bg="#e0e0e0"
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame, text="Abrir Carpeta", command=abrir_carpeta,
            font=("MS Sans Serif", 8), width=12, bg="#e0e0e0"
        ).pack(side="left", padx=5)
        
        tk.Button(
            btn_frame, text="Cerrar", command=cerrar,
            font=("MS Sans Serif", 8, "bold"), width=12, bg="#e0e0e0"
        ).pack(side="left", padx=5)

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

¿Cómo ver las nóminas?
• Use "Ver PDF Completo" para abrir todo el archivo
• Al hacer doble clic en una fila verá esa página específica

¿Cómo corregir errores?
1. Haga doble clic en la fila con error
2. Revise la nómina en la vista previa (lado izquierdo)
3. Complete o corrija los datos (lado derecho)
4. Haga clic en "Guardar"

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