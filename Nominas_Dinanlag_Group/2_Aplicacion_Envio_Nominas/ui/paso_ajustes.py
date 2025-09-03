import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import smtplib
from logic.settings import save_settings
from logic.formato_archivos import generar_ejemplo_archivo, validar_plantilla


class PasoAjustes(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        # Título principal estilo Windows clásico
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

        # Crear notebook para las pestañas
        self.notebook = ttk.Notebook(self, style="Modern.TNotebook")
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Configurar estilo para las pestañas
        self._configurar_estilos()
        
        # Crear las pestañas
        self._crear_pestaña_email()
        self._crear_pestaña_general()
        
        # Botones de acción en la parte inferior
        self._crear_botones_accion()

    def _configurar_estilos(self):
        """Configura los estilos para las pestañas modernas."""
        style = ttk.Style()
        
        # Estilo para el Notebook
        style.configure("Modern.TNotebook", background="#f0f0f0", borderwidth=0)
        style.configure("Modern.TNotebook.Tab", 
                       padding=[20, 10], 
                       font=("Segoe UI", 9, "bold"),
                       background="#e8e8e8",
                       foreground="#2c3e50")
        style.map("Modern.TNotebook.Tab",
                 background=[("selected", "#ffffff"), ("active", "#d5dbdb")],
                 foreground=[("selected", "#2980b9"), ("active", "#2c3e50")])

    def _crear_pestaña_email(self):
        """Crea la pestaña de configuración de email."""
        frame_email = ttk.Frame(self.notebook, style="Modern.TFrame")
        self.notebook.add(frame_email, text="📧 Email")
        
        # Configuración SMTP
        smtp_group = tk.LabelFrame(
            frame_email, text=" Configuración del Servidor SMTP ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        smtp_group.pack(fill="x", padx=10, pady=(10, 0))
        
        # Servidor SMTP
        tk.Label(smtp_group, text="Servidor SMTP:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=8, padx=12)
        
        self.servidor_entry = tk.Entry(smtp_group, width=35, font=("MS Sans Serif", 8))
        self.servidor_entry.grid(row=0, column=1, sticky="ew", pady=5)
        self.servidor_entry.insert(0, self.controller.config.get('SMTP', 'servidor', fallback='smtp.gmail.com'))
        
        # Puerto
        tk.Label(smtp_group, text="Puerto:", font=("Segoe UI", 9), bg="#f8f9fa").grid(
            row=0, column=2, sticky="w", pady=5, padx=(20, 10))
        
        self.puerto_entry = tk.Entry(smtp_group, width=10, font=("Segoe UI", 9), relief="solid", bd=1)
        self.puerto_entry.grid(row=0, column=3, sticky="w", pady=5)
        self.puerto_entry.insert(0, self.controller.config.get('SMTP', 'puerto', fallback='587'))
        
        smtp_group.grid_columnconfigure(1, weight=1)
        
        # Credenciales
        cred_group = tk.LabelFrame(
            frame_email, text=" Credenciales de Acceso ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        cred_group.pack(fill="x", padx=10, pady=(15, 0))
        cred_group.configure(bg="#f0f0f0")
        
        # Email
        tk.Label(cred_group, text="Email:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=8, padx=12)
        
        self.email_entry = tk.Entry(cred_group, width=40, font=("MS Sans Serif", 8))
        self.email_entry.grid(row=0, column=1, sticky="ew", pady=8, padx=(0, 12), columnspan=2)
        self.email_entry.insert(0, self.controller.config.get('Email', 'email_origen', fallback=''))
        
        # Contraseña
        tk.Label(cred_group, text="Contraseña:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=8, padx=12)
        
        self.password_entry = tk.Entry(cred_group, width=25, font=("MS Sans Serif", 8), show="*")
        self.password_entry.grid(row=1, column=1, sticky="w", pady=8, padx=(0, 10))
        self.password_entry.insert(0, self.controller.config.get('Email', 'password', fallback=''))
        
        self.show_password = tk.BooleanVar()
        toggle_btn = tk.Button(cred_group, text="👁️", command=self._toggle_password,
                              font=("MS Sans Serif", 8), width=3, relief="raised", bd=1)
        toggle_btn.grid(row=1, column=2, sticky="w", pady=8, padx=(5, 0))
        
        cred_group.grid_columnconfigure(1, weight=1)
        
        # Test de conexión
        test_frame = tk.Frame(cred_group, bg="#f0f0f0")
        test_frame.grid(row=2, column=0, columnspan=3, pady=(10, 0), sticky="ew")
        
        self.test_btn = tk.Button(test_frame, text="Probar Conexión", 
                                 command=self._test_smtp_connection,
                                 font=("MS Sans Serif", 8), relief="raised", bd=2, padx=15, pady=6)
        self.test_btn.pack(side="left", padx=(12, 0))
        
        self.test_status = tk.Label(test_frame, text="", font=("MS Sans Serif", 8), bg="#f0f0f0")
        self.test_status.pack(side="left", padx=(15, 0))
        
        # Plantilla de Email
        template_group = tk.LabelFrame(
            frame_email, text=" Plantilla de Email ",
            font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2c3e50",
            relief="solid", bd=1, padx=15, pady=10
        )
        template_group.pack(fill="both", expand=True, padx=10, pady=(15, 10))
        
        # Asunto
        tk.Label(template_group, text="Asunto:", font=("Segoe UI", 9), bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        self.asunto_entry = tk.Entry(template_group, width=60, font=("Segoe UI", 9), relief="solid", bd=1)
        self.asunto_entry.pack(fill="x", pady=(0, 10))
        self.asunto_entry.insert(0, self.controller.config.get('Email', 'asunto', 
                                fallback='Nómina correspondiente a {mes} {año}'))
        
        # Cuerpo del mensaje
        tk.Label(template_group, text="Mensaje:", font=("Segoe UI", 9), bg="#f8f9fa").pack(anchor="w", pady=(0, 5))
        
        self.mensaje_text = tk.Text(template_group, height=6, width=60, font=("Segoe UI", 9), 
                                   relief="solid", bd=1, wrap="word")
        self.mensaje_text.pack(fill="both", expand=True)
        
        mensaje_default = self.controller.config.get('Email', 'cuerpo_mensaje', fallback='''Estimado/a {nombre} {apellidos},

Le adjuntamos su nómina correspondiente al mes de {mes} de {año}.

Saludos cordiales,
Departamento de Recursos Humanos''')
        self.mensaje_text.insert("1.0", mensaje_default)
        

    def _crear_pestaña_general(self):
        """Crea la pestaña de configuración general."""
        frame_general = ttk.Frame(self.notebook)
        self.notebook.add(frame_general, text="🔧 General")
        
        # Configuración Básica
        basico_group = tk.LabelFrame(
            frame_general, text=" Configuración Básica ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        basico_group.pack(fill="x", padx=10, pady=(10, 0))
        basico_group.configure(bg="#f0f0f0")
        
        # Pausa entre emails (simplificado)
        tk.Label(basico_group, text="Pausa entre emails:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=8, padx=12)
        
        self.delay_var = tk.StringVar(value=self.controller.config.get('SMTP', 'delay_segundos', fallback='1.0'))
        delay_spin = tk.Spinbox(basico_group, from_=0.5, to=5.0, increment=0.5, width=10, textvariable=self.delay_var,
                               font=("MS Sans Serif", 8))
        delay_spin.grid(row=0, column=1, sticky="w", pady=8, padx=(0, 10))
        tk.Label(basico_group, text="segundos", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=2, sticky="w", pady=8)
        
        # Contraseña de PDFs (movido desde Email)
        tk.Label(basico_group, text="Contraseña para editar PDFs:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=8, padx=12)
        
        self.pdf_password_entry = tk.Entry(basico_group, width=20, font=("MS Sans Serif", 8), show="*")
        self.pdf_password_entry.grid(row=1, column=1, sticky="w", pady=8, padx=(0, 10))
        self.pdf_password_entry.insert(0, self.controller.config.get('PDF', 'password_autor', fallback=''))
        
        self.show_pdf_password = tk.BooleanVar()
        pdf_toggle_btn = tk.Button(basico_group, text="👁️", command=self._toggle_pdf_password,
                                  font=("MS Sans Serif", 8), width=3, relief="raised", bd=1)
        pdf_toggle_btn.grid(row=1, column=2, sticky="w", pady=8, padx=(5, 0))
        
        # Configuración de Carpetas y Archivos
        carpetas_group = tk.LabelFrame(
            frame_general, text=" Configuración de Carpetas y Archivos ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        carpetas_group.pack(fill="x", padx=10, pady=(15, 0))
        carpetas_group.configure(bg="#f0f0f0")
        
        # Carpeta de salida (igual que en Paso1)
        selector_frame = tk.Frame(carpetas_group, bg="#f0f0f0")
        selector_frame.pack(fill="x", padx=12, pady=8)
        selector_frame.grid_columnconfigure(0, weight=1)
        
        self.carpeta_salida = tk.StringVar(value=self.controller.config.get('Carpetas', 'salida', 
                                          fallback='2_nominas_individuales_encriptadas'))
        
        # Campo de texto y botón examinar estilo Windows (igual que Paso1)
        self.carpeta_entry = tk.Entry(selector_frame, textvariable=self.carpeta_salida, 
                                    font=("MS Sans Serif", 8), state="readonly")
        self.carpeta_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        
        browse_btn = tk.Button(selector_frame, text="Examinar...",
                             font=("MS Sans Serif", 8), width=12,
                             command=self._browse_output_folder,
                             relief="raised", bd=2, bg="#e0e0e0")
        browse_btn.grid(row=0, column=1)
        
        # Etiqueta descriptiva
        tk.Label(selector_frame, text="Seleccione dónde guardar las nóminas procesadas",
                font=("MS Sans Serif", 8), bg="#f0f0f0", fg="#000080", justify="left").grid(
                row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        
        # Formato de archivos
        formato_frame = tk.Frame(carpetas_group, bg="#f0f0f0")
        formato_frame.pack(fill="x", padx=12, pady=8)
        
        tk.Label(formato_frame, text="Formato de archivo:", font=("MS Sans Serif", 8), bg="#f0f0f0").pack(anchor="w")
        
        self.formato_archivo = tk.StringVar(value=self.controller.config.get('Formato', 'archivo_nomina', 
                                          fallback='{nombre}_{apellidos}_Nomina_{mes}_{año}.pdf'))
        formato_entry = tk.Entry(formato_frame, textvariable=self.formato_archivo, width=60, 
                               font=("MS Sans Serif", 8))
        formato_entry.pack(fill="x", pady=(5, 0))
        
        # Vista previa del formato
        tk.Label(formato_frame, text="Vista previa:", font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0").pack(anchor="w", pady=(10, 0))
        self.preview_label = tk.Label(formato_frame, text="", font=("MS Sans Serif", 8, "italic"), 
                                     bg="#f0f0f0", fg="#666666")
        self.preview_label.pack(anchor="w", pady=(2, 0))
        
        formato_entry.bind('<KeyRelease>', self._update_preview)
        self._update_preview()


    def _crear_botones_accion(self):
        """Crea los botones de acción en la parte inferior."""
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(fill="x", side="bottom", padx=20, pady=15)
        
        # Botón Guardar estilo Windows clásico
        guardar_btn = tk.Button(btn_frame, text="Guardar", 
                               command=self._guardar_configuracion,
                               font=("MS Sans Serif", 8), 
                               relief="raised", bd=2, padx=20, pady=8)
        guardar_btn.pack(side="right", padx=(10, 0))
        
        # Botón Cancelar estilo Windows clásico
        cancelar_btn = tk.Button(btn_frame, text="Cancelar", 
                                command=self._cancelar,
                                font=("MS Sans Serif", 8),
                                relief="raised", bd=2, padx=20, pady=8)
        cancelar_btn.pack(side="right")

    def _toggle_password(self):
        """Alterna la visibilidad de la contraseña."""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
            
    def _toggle_pdf_password(self):
        """Alterna la visibilidad de la contraseña de PDFs."""
        if self.pdf_password_entry.cget('show') == '*':
            self.pdf_password_entry.config(show="")
        else:
            self.pdf_password_entry.config(show="*")

    def _test_smtp_connection(self):
        """Prueba la conexión SMTP."""
        self.test_status.config(text="🔄 Probando...", fg="#f39c12")
        self.test_btn.config(state="disabled")
        
        def test_connection():
            try:
                servidor = self.servidor_entry.get()
                puerto = int(self.puerto_entry.get())
                email = self.email_entry.get()
                password = self.password_entry.get()
                
                server = smtplib.SMTP(servidor, puerto, timeout=10)
                server.starttls()
                server.login(email, password)
                server.quit()
                
                self.test_status.config(text="✅ Conexión exitosa", fg="#27ae60")
            except Exception as e:
                self.test_status.config(text=f"❌ Error: {str(e)[:50]}...", fg="#e74c3c")
            finally:
                self.test_btn.config(state="normal")
        
        threading.Thread(target=test_connection, daemon=True).start()

    def _browse_output_folder(self):
        """Abre el diálogo para seleccionar carpeta de salida."""
        folder = filedialog.askdirectory(
            title="Seleccionar carpeta de salida",
            initialdir=self.carpeta_salida.get()
        )
        if folder:
            self.carpeta_salida.set(folder)

    def _update_preview(self, event=None):
        """Actualiza la vista previa del formato de archivo."""
        try:
            plantilla = self.formato_archivo.get()
            ejemplo = generar_ejemplo_archivo(plantilla)
            self.preview_label.config(text=f"Ejemplo: {ejemplo}", fg="#2980b9")
        except Exception:
            self.preview_label.config(text="Formato inválido", fg="#e74c3c")


    def _guardar_configuracion(self):
        """Guarda toda la configuración."""
        try:
            # Email
            self.controller.config.set('Email', 'email_origen', self.email_entry.get())
            self.controller.config.set('Email', 'password', self.password_entry.get())
            self.controller.config.set('Email', 'asunto', self.asunto_entry.get())
            self.controller.config.set('Email', 'cuerpo_mensaje', self.mensaje_text.get("1.0", tk.END).strip())
            
            # SMTP
            self.controller.config.set('SMTP', 'servidor', self.servidor_entry.get())
            self.controller.config.set('SMTP', 'puerto', self.puerto_entry.get())
            self.controller.config.set('SMTP', 'delay_segundos', self.delay_var.get())
            
            # Archivos
            self.controller.config.set('Carpetas', 'salida', self.carpeta_salida.get())
            self.controller.config.set('Formato', 'archivo_nomina', self.formato_archivo.get())
            
            # PDF
            self.controller.config.set('PDF', 'password_autor', self.pdf_password_entry.get())
            
            # Guardar archivo
            save_settings(self.controller.config)
            
            messagebox.showinfo("Configuración Guardada", 
                              "La configuración se ha guardado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar la configuración: {e}")

    def _cancelar(self):
        """Cancela los cambios y vuelve al paso anterior."""
        self.controller.mostrar_frame("Paso1")