import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
from logic.settings import save_settings
from logic.formato_archivos import generar_ejemplo_archivo, validar_plantilla


class PasoAjustes(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        # Título principal estilo Windows
        titulo_frame = tk.Frame(self, bg="#f0f0f0")
        titulo_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            titulo_frame, text="Configuración del Sistema",
            font=("MS Sans Serif", 14, "bold"), bg="#f0f0f0", fg="#000000"
        ).pack(anchor="w")
        
        tk.Label(
            titulo_frame, text="Configure los parámetros de envío de correo electrónico y carpetas de trabajo.",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040"
        ).pack(anchor="w", pady=(5, 0))

        # Configuración de servidor SMTP estilo Windows
        smtp_frame = tk.LabelFrame(
            self, text=" Servidor de Correo Electrónico ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        smtp_frame.pack(fill="x", expand=False, pady=(0, 15))
        smtp_frame.configure(bg="#f0f0f0")

        # Grid para servidor SMTP
        tk.Label(
            smtp_frame, text="Servidor SMTP:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=0, column=0, sticky="w", pady=8, padx=12)
        
        self.servidor_entry = tk.Entry(smtp_frame, width=40, font=("MS Sans Serif", 8))
        self.servidor_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))
        self.servidor_entry.insert(0, self.controller.config.get(
            'SMTP', 'servidor', fallback='smtp.gmail.com'))

        tk.Label(
            smtp_frame, text="Puerto:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=1, column=0, sticky="w", pady=8, padx=12)
        
        self.puerto_entry = tk.Entry(smtp_frame, width=10, font=("MS Sans Serif", 8))
        self.puerto_entry.grid(row=1, column=1, sticky="w", padx=(0, 12))
        self.puerto_entry.insert(0, self.controller.config.get(
            'SMTP', 'puerto', fallback='587'))

        tk.Label(
            smtp_frame, text="Email de Origen:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=2, column=0, sticky="w", pady=8, padx=12)
        
        self.email_entry = tk.Entry(smtp_frame, width=40, font=("MS Sans Serif", 8))
        self.email_entry.grid(row=2, column=1, sticky="ew", padx=(0, 12))
        self.email_entry.insert(0, self.controller.config.get(
            'Email', 'email_origen', fallback=''))

        tk.Label(
            smtp_frame, text="Contraseña de Aplicación:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=3, column=0, sticky="w", pady=8, padx=12)
        
        self.pass_entry = tk.Entry(smtp_frame, show="*", width=40, font=("MS Sans Serif", 8))
        self.pass_entry.grid(row=3, column=1, sticky="ew", padx=(0, 12))
        self.pass_entry.insert(0, self.controller.config.get(
            'Email', 'password', fallback=''))
        
        smtp_frame.grid_columnconfigure(1, weight=1)

        # Configuración de PDFs estilo Windows
        pdf_frame = tk.LabelFrame(
            self, text=" Configuración de PDFs ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        pdf_frame.pack(fill="x", expand=False, pady=(0, 15))
        pdf_frame.configure(bg="#f0f0f0")

        tk.Label(
            pdf_frame, text="Contraseña de Edición de PDFs (obligatoria):",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000"
        ).grid(row=0, column=0, sticky="w", pady=8, padx=12)
        
        # Frame para entrada y botón de mostrar/ocultar
        pass_frame = tk.Frame(pdf_frame, bg="#f0f0f0")
        pass_frame.grid(row=0, column=1, sticky="ew", padx=(0, 12), pady=8)
        pass_frame.grid_columnconfigure(0, weight=1)
        
        self.autor_pass_entry = tk.Entry(pass_frame, show="*", width=20, font=("MS Sans Serif", 8))
        self.autor_pass_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.autor_pass_entry.insert(0, self.controller.config.get(
            'PDF', 'password_autor', fallback=''))
        
        self.show_pass_btn = tk.Button(
            pass_frame, text="👁", width=3,
            font=("MS Sans Serif", 8), 
            command=self.toggle_password_visibility,
            relief="raised", bd=1, bg="#e8e8e8"
        )
        self.show_pass_btn.grid(row=0, column=1)
        
        self.pass_visible = False  # Estado de visibilidad
        
        # Descripción más clara
        desc_frame = tk.Frame(pdf_frame, bg="#f0f0f0")
        desc_frame.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8))
        
        tk.Label(
            desc_frame, text="Contraseña de edición de PDF",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040"
        ).pack(anchor="w")

        pdf_frame.grid_columnconfigure(1, weight=1)

        # Formato de Archivos de Nómina estilo Windows
        formato_frame = tk.LabelFrame(
            self, text=" Formato de Nombres de Archivo ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        formato_frame.pack(fill="x", expand=False, pady=(0, 15))
        formato_frame.configure(bg="#f0f0f0")

        # Formato de archivo
        tk.Label(
            formato_frame, text="Formato del nombre de archivo:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))

        self.formato_archivo_entry = tk.Entry(
            formato_frame, font=("MS Sans Serif", 8), width=50,
            relief="sunken", bd=1
        )
        self.formato_archivo_entry.grid(row=0, column=1, sticky="ew", padx=(5, 10), pady=(10, 0))
        self.formato_archivo_entry.insert(0, self.controller.config.get(
            'Formato', 'archivo_nomina', fallback='{NOMBRE}_{APELLIDO}_Nomina_{mes}_{año}.pdf'))
            
        # Binding para actualizar ejemplo en tiempo real
        self.formato_archivo_entry.bind('<KeyRelease>', lambda e: self.after(100, self.actualizar_ejemplo_archivo))

        # Botón de vista previa
        formato_botones_frame = tk.Frame(formato_frame, bg="#f0f0f0")
        formato_botones_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 0))

        tk.Button(
            formato_botones_frame, text="Vista Previa",
            font=("MS Sans Serif", 8), width=15, height=1,
            command=self.mostrar_vista_previa_archivo,
            relief="raised", bd=1, bg="#e8f4fd"
        ).pack(anchor="w")

        # Descripción de variables
        desc_formato_frame = tk.Frame(formato_frame, bg="#f0f0f0")
        desc_formato_frame.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        tk.Label(
            desc_formato_frame, text="Variables disponibles:",
            font=("MS Sans Serif", 7, "bold"), bg="#f0f0f0", fg="#000000"
        ).pack(anchor="w")
        
        variables_texto = (
            "  • {NOMBRE} - Nombre en mayúsculas (ej: JOSUNE)\n"
            "  • {APELLIDO} - Apellido en mayúsculas (ej: ANGOITIS)\n" 
            "  • {nombre} - Nombre normal (ej: Josune)\n"
            "  • {apellido} - Apellido normal (ej: Angoitis)\n"
            "  • {mes} - Mes actual (ej: junio)\n"
            "  • {año} - Año actual (ej: 2025)\n"
            "  • {MES} - Mes en mayúsculas (ej: JUNIO)"
        )
        
        tk.Label(
            desc_formato_frame, text=variables_texto,
            font=("MS Sans Serif", 7), bg="#f0f0f0", fg="#404040", justify="left"
        ).pack(anchor="w", padx=(5, 0))

        # Ejemplo en tiempo real
        ejemplo_frame = tk.Frame(formato_frame, bg="#f9f9f9", relief="sunken", bd=1)
        ejemplo_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=10, pady=(5, 10))

        tk.Label(
            ejemplo_frame, text="Ejemplo:",
            font=("MS Sans Serif", 7, "bold"), bg="#f9f9f9", fg="#000000"
        ).pack(anchor="w", padx=5, pady=(5, 0))

        self.ejemplo_archivo_label = tk.Label(
            ejemplo_frame, text="",
            font=("MS Sans Serif", 8), bg="#f9f9f9", fg="#0066cc"
        )
        self.ejemplo_archivo_label.pack(anchor="w", padx=5, pady=(0, 5))

        # Actualizar ejemplo inicial
        self.actualizar_ejemplo_archivo()

        formato_frame.grid_columnconfigure(1, weight=1)

        # Configuración de carpetas estilo Windows
        carpetas_frame = tk.LabelFrame(
            self, text=" Carpetas de Trabajo ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        carpetas_frame.pack(fill="x", expand=False, pady=(0, 15))
        carpetas_frame.configure(bg="#f0f0f0")

        tk.Label(
            carpetas_frame, text="Carpeta de Salida para PDFs:",
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000000"
        ).grid(row=0, column=0, sticky="w", pady=8, padx=12)
        
        carpeta_frame = tk.Frame(carpetas_frame, bg="#f0f0f0")
        carpeta_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 8))
        
        self.carpeta_entry = tk.Entry(carpeta_frame, width=50, font=("MS Sans Serif", 8))
        self.carpeta_entry.pack(side="left", fill="x", expand=True)
        self.carpeta_entry.insert(0, self.controller.config.get(
            'Carpetas', 'salida', fallback=os.path.join(os.getcwd(), 'nominas_individuales')))
        
        self.btn_carpeta = tk.Button(
            carpeta_frame, text="Examinar...",
            font=("MS Sans Serif", 8), width=12,
            command=self.seleccionar_carpeta,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_carpeta.pack(side="right", padx=(8, 0))

        carpetas_frame.grid_columnconfigure(0, weight=1)

        # Información adicional estilo Windows
        info_frame = tk.LabelFrame(
            self, text=" Información ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        info_frame.pack(fill="x", expand=False, pady=(0, 20))
        info_frame.configure(bg="#f0f0f0")

        info_text = (
            "• Para Gmail, use una contraseña de aplicación específica.\n"
            "• Asegúrese de que la autenticación en dos pasos esté activada.\n"
            "• La carpeta de salida se creará automáticamente si no existe."
        )
        tk.Label(
            info_frame, text=info_text,
            font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#404040",
            justify="left", anchor="w"
        ).pack(fill="x", padx=12, pady=8)

        # Botones estilo Windows
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # Separador estilo Windows
        separator = tk.Frame(btn_frame, height=1, bg="#c0c0c0", relief="sunken", bd=1)
        separator.pack(fill="x", pady=(0, 10))
        
        buttons_container = tk.Frame(btn_frame, bg="#f0f0f0")
        buttons_container.pack(side="right")
        
        self.btn_volver = tk.Button(
            buttons_container, text="< Volver",
            font=("MS Sans Serif", 8), width=12, height=2,
            command=lambda: controller.mostrar_frame("Paso1"),
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_volver.pack(side="left", padx=(0, 8))
        
        self.btn_guardar = tk.Button(
            buttons_container, text="Guardar",
            font=("MS Sans Serif", 8, "bold"), width=12, height=2,
            command=self.guardar_configuracion,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_guardar.pack(side="left")

    def toggle_password_visibility(self):
        """Alterna la visibilidad de la contraseña de autor"""
        if self.pass_visible:
            self.autor_pass_entry.config(show="*")
            self.show_pass_btn.config(text="👁")
            self.pass_visible = False
        else:
            self.autor_pass_entry.config(show="")
            self.show_pass_btn.config(text="🙈")
            self.pass_visible = True

    def seleccionar_carpeta(self):
        """Abre diálogo para seleccionar carpeta de salida"""
        carpeta = filedialog.askdirectory(
            title="Seleccionar Carpeta de Salida",
            initialdir=self.carpeta_entry.get() or os.getcwd()
        )
        if carpeta:
            self.carpeta_entry.delete(0, tk.END)
            self.carpeta_entry.insert(0, carpeta)

    def guardar_configuracion(self):
        """Guarda toda la configuración con validación"""
        # Validar campos obligatorios
        if not self.email_entry.get().strip():
            messagebox.showerror(
                "Error de Configuración",
                "El email de origen es obligatorio."
            )
            return
            
        if not self.pass_entry.get().strip():
            messagebox.showerror(
                "Error de Configuración", 
                "La contraseña de email es obligatoria."
            )
            return
            
        if not self.autor_pass_entry.get().strip():
            messagebox.showerror(
                "Error de Configuración",
                "La contraseña de edición de PDFs es obligatoria.\n\n"
                "Esta contraseña la necesitará para editar los PDFs generados."
            )
            return

        try:
            # Validar puerto
            puerto = int(self.puerto_entry.get())
            if puerto <= 0 or puerto > 65535:
                raise ValueError()
        except ValueError:
            messagebox.showerror(
                "Error de Configuración",
                "El puerto debe ser un número válido entre 1 y 65535."
            )
            return

        # Crear carpeta si no existe
        carpeta_salida = self.carpeta_entry.get().strip()
        if carpeta_salida:
            try:
                os.makedirs(carpeta_salida, exist_ok=True)
            except OSError as e:
                messagebox.showerror(
                    "Error de Carpeta",
                    f"No se pudo crear la carpeta:\n{e}"
                )
                return

        # Validar formato de archivo
        formato_archivo = self.formato_archivo_entry.get().strip()
        if not formato_archivo:
            messagebox.showerror(
                "Error de Configuración",
                "El formato de nombre de archivo es obligatorio."
            )
            return
            
        if not formato_archivo.endswith('.pdf'):
            formato_archivo += '.pdf'

        # Guardar configuración
        if 'SMTP' not in self.controller.config:
            self.controller.config['SMTP'] = {}
        if 'Carpetas' not in self.controller.config:
            self.controller.config['Carpetas'] = {}
        if 'PDF' not in self.controller.config:
            self.controller.config['PDF'] = {}
        if 'Formato' not in self.controller.config:
            self.controller.config['Formato'] = {}

        self.controller.config.set('SMTP', 'servidor', self.servidor_entry.get())
        self.controller.config.set('SMTP', 'puerto', self.puerto_entry.get())
        self.controller.config.set('Email', 'email_origen', self.email_entry.get())
        self.controller.config.set('Email', 'password', self.pass_entry.get())
        self.controller.config.set('PDF', 'password_autor', self.autor_pass_entry.get())
        self.controller.config.set('Formato', 'archivo_nomina', formato_archivo)
        self.controller.config.set('Carpetas', 'salida', carpeta_salida)

        try:
            save_settings(self.controller.config)
            messagebox.showinfo(
                "Configuración Guardada",
                "La configuración se ha guardado correctamente.\n\n"
                "Los cambios se aplicarán en el próximo envío."
            )
            self.controller.mostrar_frame("Paso1")
        except Exception as e:
            messagebox.showerror(
                "Error al Guardar",
                f"No se pudo guardar la configuración:\n{e}"
            )

    def mostrar_vista_previa_archivo(self):
        """Muestra vista previa del nombre de archivo generado."""
        plantilla = self.formato_archivo_entry.get().strip()
        
        # Validar plantilla
        es_valida, mensaje = validar_plantilla(plantilla)
        if not es_valida:
            messagebox.showerror("Error en Formato", mensaje)
            return
            
        # Generar ejemplos
        ejemplo1 = generar_ejemplo_archivo(plantilla)
        
        messagebox.showinfo(
            "Vista Previa de Archivo",
            f"Formato: {plantilla}\n\n"
            f"Ejemplo con 'María García':\n{ejemplo1}\n\n"
            "Los nombres reales se generarán automáticamente "
            "según los datos de cada empleado."
        )
        
    def actualizar_ejemplo_archivo(self):
        """Actualiza el ejemplo mostrado en tiempo real."""
        try:
            plantilla = self.formato_archivo_entry.get().strip()
            if plantilla:
                ejemplo = generar_ejemplo_archivo(plantilla)
                self.ejemplo_archivo_label.config(text=ejemplo, fg="#0066cc")
            else:
                self.ejemplo_archivo_label.config(text="(ingrese un formato)", fg="#888888")
        except Exception:
            self.ejemplo_archivo_label.config(text="(formato inválido)", fg="#cc0000")
            
    def aplicar_formato_predefinido(self, formato):
        """Aplica un formato predefinido y actualiza el ejemplo."""
        self.formato_archivo_entry.delete(0, 'end')
        self.formato_archivo_entry.insert(0, formato)
        self.actualizar_ejemplo_archivo()