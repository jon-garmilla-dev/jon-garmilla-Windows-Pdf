import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import smtplib
import webbrowser
from logic.settings import save_settings
from logic.formato_archivos import generar_ejemplo_archivo


class ToolTipButton:
    """Clase para crear tooltips activados por botón."""
    def __init__(self, button, text):
        self.button = button
        self.text = text
        self.tipwindow = None
        self.button.bind("<Button-1>", self.toggle_tooltip)
        
    def toggle_tooltip(self, event=None):
        if self.tipwindow:
            self.hide_tooltip()
        else:
            self.show_tooltip()
            
    def show_tooltip(self, event=None):
        if self.tipwindow or not self.text:
            return
        
        # Posicionar cerca del botón
        x = self.button.winfo_rootx() + 30
        y = self.button.winfo_rooty() + 25
        
        self.tipwindow = tw = tk.Toplevel(self.button)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        
        label = tk.Label(
            tw, text=self.text, justify=tk.LEFT,
            background="#ffffe0", relief=tk.SOLID, borderwidth=1,
            font=("MS Sans Serif", 8, "normal"), wraplength=300,
            padx=8, pady=6)
        label.pack()
        
        # Eventos para cerrar el tooltip cuando se sale con el cursor
        tw.bind("<Leave>", self.hide_tooltip)
        label.bind("<Leave>", self.hide_tooltip)
        
        # Auto-ocultar después de 8 segundos
        self.auto_hide_id = tw.after(8000, self.hide_tooltip)

    def hide_tooltip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            # Cancelar el auto-hide si existe
            if hasattr(self, 'auto_hide_id') and self.auto_hide_id:
                try:
                    tw.after_cancel(self.auto_hide_id)
                except tk.TclError:
                    pass
            tw.destroy()


class PasoAjustes(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller

        # Título principal estilo Windows clásico
        titulo_frame = tk.Frame(self, bg="#f0f0f0")
        titulo_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            titulo_frame,
            text="Configuración del Sistema",
            font=("MS Sans Serif", 14, "bold"),
            bg="#f0f0f0",
            fg="#000000").pack(anchor="w")

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
        self.notebook.add(frame_email, text="Email")
        
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
        self.servidor_entry.insert(
            0,
            self.controller.config.get(
                'SMTP', 'servidor', fallback='smtp.gmail.com'))
        
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
        self.email_entry.grid(
            row=0, column=1, sticky="ew", pady=8, padx=(0, 12), columnspan=2)
        self.email_entry.insert(
            0, self.controller.config.get('Email', 'email_origen', fallback=''))
        
        # Contraseña
        tk.Label(cred_group, text="Contraseña:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=8, padx=12)
        
        # Frame para contraseña + botón ojo
        password_frame = tk.Frame(cred_group, bg="#f0f0f0")
        password_frame.grid(row=1, column=1, sticky="w", pady=8, padx=(0, 10))
        
        self.password_entry = tk.Entry(password_frame, width=20, font=("MS Sans Serif", 8), show="*")
        self.password_entry.pack(side="left")
        self.password_entry.insert(
            0, self.controller.config.get('Email', 'password', fallback=''))
        
        self.show_password = tk.BooleanVar()
        toggle_btn = tk.Button(password_frame, text="👁", command=self._toggle_password,
                              font=("MS Sans Serif", 10), width=2, relief="raised", bd=1)
        toggle_btn.pack(side="left", padx=(5, 0))
        
        # Botón de ayuda para credenciales
        help_btn_credenciales = tk.Button(password_frame, text="?", 
                                        font=("MS Sans Serif", 8), width=2,
                                        relief="raised", bd=2)
        help_btn_credenciales.pack(side="left", padx=(5, 0))
        
        # Tooltip con información sobre cómo obtener credenciales
        credenciales_tooltip = """¿Dónde obtener las credenciales?

Para Gmail:
1. Ve a tu cuenta de Google
2. Seguridad → Verificación en 2 pasos (debe estar activada)
3. Contraseñas de aplicaciones
4. Selecciona "Correo" → "Otro"
5. Escribe "Sistema Nóminas"
6. Usa la contraseña generada (16 caracteres)

🔗 Acceso directo Gmail: myaccount.google.com/security

Para Outlook/Hotmail:
1. Inicia sesión en outlook.com
2. Configuración → Ver toda la configuración
3. Correo → Sincronizar correo
4. Contraseñas de aplicación → Crear contraseña
5. Usa la contraseña generada

🔗 Acceso directo Outlook: account.microsoft.com/security

¡NUNCA uses tu contraseña personal del email!"""
        ToolTipButton(help_btn_credenciales, credenciales_tooltip)
        
        # Link directo a Gmail - texto azul como hiperlink
        gmail_link = tk.Label(password_frame, text="Gmail →", 
                             font=("MS Sans Serif", 8, "underline"), 
                             fg="#0066cc", bg="#f0f0f0", cursor="hand2")
        gmail_link.pack(side="left", padx=(10, 0))
        gmail_link.bind("<Button-1>", self._abrir_gmail_security)
        
        # Test de conexión - en la misma línea que la contraseña, a la derecha
        self.test_btn = tk.Button(
            cred_group, text="Probar Conexión",
            command=self._test_smtp_connection,
            font=("MS Sans Serif", 8), relief="raised",
            bd=2, padx=15, pady=6)
        self.test_btn.grid(row=1, column=2, sticky="e", pady=8, padx=(20, 12))
        
        self.test_status = tk.Label(cred_group, text="", font=("MS Sans Serif", 8), bg="#f0f0f0")
        self.test_status.grid(row=2, column=2, sticky="e", pady=(5, 8), padx=(20, 12))
        
        cred_group.grid_columnconfigure(1, weight=1)
        
        # Plantilla de Email
        template_group = tk.LabelFrame(
            frame_email, text=" Plantilla de Email ",
            font=("Segoe UI", 10, "bold"), bg="#f8f9fa", fg="#2c3e50",
            relief="solid", bd=1, padx=15, pady=10
        )
        template_group.pack(
            fill="both", expand=True, padx=10, pady=(15, 10))
        
        # Asunto
        asunto_label_frame = tk.Frame(template_group, bg="#f8f9fa")
        asunto_label_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(asunto_label_frame, text="Asunto:", font=("Segoe UI", 9), bg="#f8f9fa").pack(side="left", anchor="w")
        
        # Botón de ayuda para asunto - mismo estilo que el botón Guardar
        help_btn_asunto = tk.Button(asunto_label_frame, text="?", 
                                  font=("MS Sans Serif", 8), width=2,
                                  relief="raised", bd=2)
        help_btn_asunto.pack(side="left", padx=(10, 0))
        
        # Tooltip para variables de email
        email_tooltip = """Variables disponibles para asunto y mensaje:

{nombre} - Nombre del empleado (ej: Juan)
{apellidos} - Apellidos del empleado (ej: García López)
{mes} - Mes actual (ej: septiembre)
{año} - Año actual (ej: 2025)

Ejemplo asunto: Nómina de {nombre} - {mes} {año}
Resultado: Nómina de Juan - septiembre 2025

Ejemplo mensaje: Estimado/a {nombre} {apellidos}...
Resultado: Estimado/a Juan García López..."""
        ToolTipButton(help_btn_asunto, email_tooltip)
        
        self.asunto_entry = tk.Entry(template_group, width=60, font=("Segoe UI", 9), relief="solid", bd=1)
        self.asunto_entry.pack(fill="x", pady=(0, 10))
        self.asunto_entry.insert(
            0, self.controller.config.get(
                'Email', 'asunto',
                fallback='Nómina correspondiente a {mes} {año}'))
        
        # Cuerpo del mensaje
        mensaje_label_frame = tk.Frame(template_group, bg="#f8f9fa")
        mensaje_label_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(mensaje_label_frame, text="Mensaje:", font=("Segoe UI", 9), bg="#f8f9fa").pack(side="left", anchor="w")
        
        # Botón de ayuda para mensaje - mismo estilo que el botón Guardar
        help_btn_mensaje = tk.Button(mensaje_label_frame, text="?", 
                                   font=("MS Sans Serif", 8), width=2,
                                   relief="raised", bd=2)
        help_btn_mensaje.pack(side="left", padx=(10, 0))
        
        # Mismo tooltip que el asunto (variables iguales)
        ToolTipButton(help_btn_mensaje, email_tooltip)
        
        self.mensaje_text = tk.Text(template_group, height=6, width=60, font=("Segoe UI", 9), 
                                   relief="solid", bd=1, wrap="word")
        self.mensaje_text.pack(fill="both", expand=True)
        
        mensaje_default = self.controller.config.get(
            'Email', 'cuerpo_mensaje',
            fallback='''Estimado/a {nombre} {apellidos},

Le adjuntamos su nómina correspondiente al mes de {mes} de {año}.

Saludos cordiales,
Departamento de Recursos Humanos''')
        self.mensaje_text.insert("1.0", mensaje_default)
        

    def _crear_pestaña_general(self):
        """Crea la pestaña de configuración general."""
        frame_general = ttk.Frame(self.notebook)
        self.notebook.add(frame_general, text="General")
        
        # Configuración Básica
        basico_group = tk.LabelFrame(
            frame_general, text=" Configuración Básica ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0",
            fg="#000000", relief="groove", bd=2)
        basico_group.pack(fill="x", padx=10, pady=(10, 0))
        basico_group.configure(bg="#f0f0f0")
        
        # Pausa entre emails (simplificado)
        tk.Label(basico_group, text="Pausa entre emails:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=0, sticky="w", pady=8, padx=12)
        
        self.delay_var = tk.StringVar(
            value=self.controller.config.get(
                'SMTP', 'delay_segundos', fallback='1.0'))
        delay_spin = tk.Spinbox(
            basico_group, from_=0.5, to=5.0, increment=0.5,
            width=10, textvariable=self.delay_var,
            font=("MS Sans Serif", 8))
        delay_spin.grid(row=0, column=1, sticky="w", pady=8, padx=(0, 10))
        tk.Label(basico_group, text="segundos", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=0, column=2, sticky="w", pady=8)
        
        # Contraseña de PDFs (movido desde Email)
        tk.Label(basico_group, text="Contraseña para editar PDFs:", font=("MS Sans Serif", 8), bg="#f0f0f0").grid(
            row=1, column=0, sticky="w", pady=8, padx=12)
        
        # Frame para contraseña PDF + botón ojo
        pdf_password_frame = tk.Frame(basico_group, bg="#f0f0f0")
        pdf_password_frame.grid(row=1, column=1, sticky="w", pady=8, padx=(0, 10))
        
        self.pdf_password_entry = tk.Entry(pdf_password_frame, width=15, font=("MS Sans Serif", 8), show="*")
        self.pdf_password_entry.pack(side="left")
        self.pdf_password_entry.insert(
            0, self.controller.config.get('PDF', 'password_autor', fallback=''))
        
        self.show_pdf_password = tk.BooleanVar()
        pdf_toggle_btn = tk.Button(pdf_password_frame, text="👁", command=self._toggle_pdf_password,
                                  font=("MS Sans Serif", 10), width=2, relief="raised", bd=1)
        pdf_toggle_btn.pack(side="left", padx=(20, 0))
        
        # Configuración de Carpetas y Archivos
        carpetas_group = tk.LabelFrame(
            frame_general, text=" Configuración de Carpetas y Archivos ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0",
            fg="#000000", relief="groove", bd=2)
        carpetas_group.pack(fill="x", padx=10, pady=(15, 0))
        carpetas_group.configure(bg="#f0f0f0")
        
        # Carpeta de salida (igual que en Paso1)
        selector_frame = tk.Frame(carpetas_group, bg="#f0f0f0")
        selector_frame.pack(fill="x", padx=12, pady=8)
        selector_frame.grid_columnconfigure(0, weight=1)
        
        self.carpeta_salida = tk.StringVar(
            value=self.controller.config.get(
                'Carpetas', 'salida',
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
        tk.Label(
            selector_frame,
            text="Seleccione dónde guardar las nóminas procesadas",
            font=("MS Sans Serif", 8), bg="#f0f0f0",
            fg="#000080", justify="left").grid(
                row=1, column=0, columnspan=2, sticky="w", pady=(8, 0))
        
        # Formato de archivos
        formato_frame = tk.Frame(carpetas_group, bg="#f0f0f0")
        formato_frame.pack(fill="x", padx=12, pady=8)
        
        # Frame para etiqueta y botón de ayuda
        formato_label_frame = tk.Frame(formato_frame, bg="#f0f0f0")
        formato_label_frame.pack(fill="x")
        
        tk.Label(formato_label_frame, text="Formato de archivo:", font=("MS Sans Serif", 8), bg="#f0f0f0").pack(side="left", anchor="w")
        
        # Botón de ayuda para formato de archivo - mismo estilo que el botón Guardar
        help_btn_formato = tk.Button(formato_label_frame, text="?", 
                                   font=("MS Sans Serif", 8), width=2,
                                   relief="raised", bd=2)
        help_btn_formato.pack(side="left", padx=(10, 0))
        
        # Tooltip para formato de archivo
        formato_tooltip = """Variables disponibles para el formato de archivo:

{NOMBRE} - Nombre en mayúsculas (ej: JUAN)
{APELLIDO} - Apellido en mayúsculas (ej: GARCIA)
{nombre} - Nombre normal (ej: Juan)
{apellido} - Apellido normal (ej: García)
{mes} - Mes actual en minúsculas (ej: septiembre)
{MES} - Mes actual en mayúsculas (ej: SEPTIEMBRE)
{año} - Año actual (ej: 2025)

Ejemplo: {NOMBRE}_{APELLIDO}_Nomina_{mes}_{año}.pdf
Resultado: JUAN_GARCIA_Nomina_septiembre_2025.pdf"""
        ToolTipButton(help_btn_formato, formato_tooltip)
        
        self.formato_archivo = tk.StringVar(
            value=self.controller.config.get(
                'Formato', 'archivo_nomina',
                fallback='{nombre}_{apellidos}_Nomina_{mes}_{año}.pdf'))
        formato_entry = tk.Entry(
            formato_frame, textvariable=self.formato_archivo, width=60,
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
        guardar_btn = tk.Button(btn_frame,
                               text="Guardar",
                               command=self._guardar_configuracion,
                               font=("MS Sans Serif", 8),
                               relief="raised",
                               bd=2,
                               padx=20,
                               pady=8)
        guardar_btn.pack(side="right", padx=(10, 0))
        
        # Botón Cancelar estilo Windows clásico
        cancelar_btn = tk.Button(btn_frame,
                                text="Cancelar",
                                command=self._cancelar,
                                font=("MS Sans Serif", 8),
                                relief="raised",
                                bd=2,
                                padx=20,
                                pady=8)
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
        self.test_status.config(text="Probando...", fg="#f39c12")
        self.test_btn.config(state="disabled")
        threading.Thread(
            target=self._test_connection_thread, daemon=True).start()

    def _test_connection_thread(self):
        try:
            servidor = self.servidor_entry.get()
            puerto = int(self.puerto_entry.get())
            email = self.email_entry.get()
            password = self.password_entry.get()

            server = smtplib.SMTP(servidor, puerto, timeout=10)
            server.starttls()
            server.login(email, password)
            server.quit()

            self.test_status.config(text="OK - Conexión exitosa", fg="#27ae60")
        except Exception as e:
            self.test_status.config(
                text=f"ERROR - Error: {str(e)[:50]}...", fg="#e74c3c")
        finally:
            self.test_btn.config(state="normal")

    def _browse_output_folder(self):
        folder = filedialog.askdirectory(
            parent=self,
            title="Seleccionar carpeta de salida",
            initialdir=self.carpeta_salida.get())
        if folder:
            self.carpeta_salida.set(folder)

    def _update_preview(self, event=None):
        try:
            plantilla = self.formato_archivo.get()
            ejemplo = generar_ejemplo_archivo(plantilla)
            self.preview_label.config(
                text=f"Ejemplo: {ejemplo}", fg="#2980b9")
        except Exception:
            self.preview_label.config(text="Formato inválido", fg="#e74c3c")

    def _guardar_configuracion(self):
        try:
            self._set_config_values()
            save_settings(self.controller.config)
            messagebox.showinfo(
                "Configuración Guardada",
                "La configuración se ha guardado correctamente.",
                parent=self)
        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al guardar la configuración: {e}",
                parent=self)

    def _set_config_values(self):
        self.controller.config.set(
            'Email', 'email_origen', self.email_entry.get())
        self.controller.config.set(
            'Email', 'password', self.password_entry.get())
        self.controller.config.set(
            'Email', 'asunto', self.asunto_entry.get())
        self.controller.config.set(
            'Email', 'cuerpo_mensaje',
            self.mensaje_text.get("1.0", tk.END).strip())
        self.controller.config.set(
            'SMTP', 'servidor', self.servidor_entry.get())
        self.controller.config.set(
            'SMTP', 'puerto', self.puerto_entry.get())
        self.controller.config.set(
            'SMTP', 'delay_segundos', self.delay_var.get())
        self.controller.config.set(
            'Carpetas', 'salida', self.carpeta_salida.get())
        self.controller.config.set(
            'Formato', 'archivo_nomina', self.formato_archivo.get())
        self.controller.config.set(
            'PDF', 'password_autor', self.pdf_password_entry.get())

    def _abrir_gmail_security(self, event=None):
        """Abre la página de seguridad de Gmail en el navegador."""
        try:
            webbrowser.open("https://myaccount.google.com/security")
        except Exception as e:
            messagebox.showerror(
                "Error", f"No se pudo abrir el navegador: {e}",
                parent=self)

    def _cancelar(self):
        self.controller.mostrar_frame("Paso1")
