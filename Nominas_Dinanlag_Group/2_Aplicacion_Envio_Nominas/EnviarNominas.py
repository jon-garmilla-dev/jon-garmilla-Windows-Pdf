import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import fitz  # PyMuPDF
import re
import os
import smtplib
import threading
import configparser
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pikepdf

# --- CONFIGURACIÓN Y LÓGICA DE BACKEND ---

SETTINGS_FILE = 'settings.ini'


def load_settings():
    """Carga la configuración desde settings.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if 'Email' not in config:
        config['Email'] = {'email_origen': '', 'password': ''}
    return config


def save_settings(config):
    """Guarda la configuración en settings.ini."""
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)


def leer_cabeceras_empleados(filepath):
    """Lee solo las cabeceras de un archivo CSV o Excel."""
    try:
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath, nrows=0).columns.tolist()
        elif filepath.endswith(('.xlsx', '.xls')):
            return pd.read_excel(filepath, nrows=0).columns.tolist()
        else:
            return []
    except Exception:
        return []


def leer_archivo_empleados(filepath):
    """Lee un archivo de empleados, detectando si es CSV o Excel."""
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Formato de archivo no soportado.")


def analizar_archivos(pdf_path, empleados_path, columnas_map):
    """Analiza los archivos con el mapeo de columnas y devuelve una lista de tareas."""
    try:
        df = leer_archivo_empleados(empleados_path)
        # Validar que las columnas mapeadas existen en el DataFrame
        for col_key, col_name in columnas_map.items():
            if col_name not in df.columns:
                raise ValueError(
                    f"La columna '{col_name}' asignada a '{col_key}' no se "
                    f"encuentra en el archivo."
                )
    except Exception as e:
        return {"error": f"Error al leer el archivo de empleados:\n{e}"}

    doc_maestro = fitz.open(pdf_path)
    tareas = []
    
    for num_pagina in range(len(doc_maestro)):
        texto_pagina = doc_maestro.load_page(num_pagina).get_text()
        nif_match = re.search(r'\b(\d{8}[A-Z])\b', texto_pagina)
        
        tarea = {
            "pagina": num_pagina + 1, "nif": "N/A", "nombre": "N/A",
            "email": "N/A", "status": "⚠️ Sin NIF en PDF"
        }
        if nif_match:
            nif = nif_match.group(1)
            tarea["nif"] = nif
            # Usar el mapeo de columnas para la búsqueda
            info = df[df[columnas_map["nif"]] == nif]
            if not info.empty:
                tarea.update({
                    "nombre": info.iloc[0][columnas_map["nombre"]],
                    "email": info.iloc[0][columnas_map["email"]],
                    "status": "✅ OK"
                })
            else:
                tarea["status"] = "❌ NIF no encontrado en la lista"
        tareas.append(tarea)
        
    doc_maestro.close()
    return {"tareas": tareas}


def enviar_nominas_worker(
    pdf_path, tareas, config, log_callback, progress_callback
):
    """Worker que procesa y envía las nóminas en un hilo separado."""
    try:
        email_origen = config.get('Email', 'email_origen')
        password = config.get('Email', 'password')
        
        if not email_origen or not password:
            raise ValueError("Credenciales de email no configuradas.")

        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 587
        
        log_callback(f"Conectando a {servidor_smtp}...")
        server = smtplib.SMTP(servidor_smtp, puerto_smtp)
        server.starttls()
        server.login(email_origen, password)
        log_callback("Conexión exitosa.")

        doc_maestro = fitz.open(pdf_path)
        tareas_a_enviar = [t for t in tareas if t['status'] == '✅ OK']
        total_tareas = len(tareas_a_enviar)
        
        output_dir = "nominas_individuales"
        os.makedirs(output_dir, exist_ok=True)

        for i, tarea in enumerate(tareas_a_enviar):
            nombre = tarea['nombre']
            nif = tarea['nif']
            email_destino = tarea['email']
            
            log_callback(f"Procesando nómina para {nombre} ({i+1}/{total_tareas})...")

            # 1. Extraer y guardar PDF individual
            doc_individual = fitz.open()
            doc_individual.insert_pdf(
                doc_maestro, from_page=tarea['pagina'] - 1,
                to_page=tarea['pagina'] - 1)
            
            temp_pdf_path = os.path.join(output_dir, f"temp_{nif}.pdf")
            doc_individual.save(temp_pdf_path)
            doc_individual.close()

            # 2. Encriptar el PDF
            pdf_encriptado_path = os.path.join(
                output_dir, f"nomina_{nombre.replace(' ', '_')}.pdf")
            with pikepdf.open(temp_pdf_path) as pdf:
                pdf.save(
                    pdf_encriptado_path,
                    encryption=pikepdf.Encryption(owner=nif, user=nif, R=4)
                )
            os.remove(temp_pdf_path)

            # 3. Enviar por correo
            msg = MIMEMultipart()
            msg['From'] = email_origen
            msg['To'] = email_destino
            msg['Subject'] = (
                f"Tu nómina de {datetime.now().strftime('%B %Y')}")
            
            cuerpo = (
                f"Hola {nombre},\n\nAdjuntamos tu nómina. "
                f"La contraseña para abrir el archivo es tu NIF.\n\nSaludos.")
            msg.attach(MIMEText(cuerpo, 'plain'))

            with open(pdf_encriptado_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f"attachment; filename= {os.path.basename(pdf_encriptado_path)}"
            )
            msg.attach(part)
            
            server.send_message(msg)
            log_callback(f"Correo enviado a {email_destino}.")
            os.remove(pdf_encriptado_path)
            
            progress_callback((i + 1) / total_tareas * 100)

        server.quit()
        log_callback("\n¡Proceso completado! Todos los correos han sido enviados.")
    except Exception as e:
        log_callback(f"\nERROR: {e}")
    finally:
        # Asegurarse de que el botón se reactive
        progress_callback(-1)


# --- INTERFAZ GRÁFICA (FRONTEND) ---

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
        self.pasos_labels["Paso1"].pack(fill="x", padx=20, pady=5, side=tk.TOP)
        self.pasos_labels["Paso2"].pack(fill="x", padx=20, pady=5, side=tk.TOP)
        self.pasos_labels["Paso3"].pack(fill="x", padx=20, pady=5, side=tk.TOP)
        self.pasos_labels["PasoAjustes"].pack(fill="x", padx=20, pady=10, side=tk.BOTTOM)


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


class Paso1(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # --- Layout ---
        self.grid_columnconfigure(0, weight=1)
        
        tk.Label(
            self, text="Paso 1: Selección y Mapeo de Archivos",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, pady=(0, 20), sticky="w")

        # --- Selección de Archivos ---
        files_frame = ttk.LabelFrame(
            self, text=" 1. Seleccione los archivos ")
        files_frame.grid(row=1, column=0, sticky="ew", pady=5)
        files_frame.grid_columnconfigure(1, weight=1)

        tk.Button(
            files_frame, text="Seleccionar PDF de Nóminas...",
            command=self.seleccionar_pdf
        ).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.pdf_label = tk.Label(
            files_frame, textvariable=self.controller.pdf_path,
            wraplength=500, justify="left")
        self.pdf_label.grid(row=0, column=1, sticky="ew", padx=10)

        tk.Button(
            files_frame, text="Seleccionar Archivo de Empleados...",
            command=self.seleccionar_empleados
        ).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.empleados_label = tk.Label(
            files_frame, textvariable=self.controller.empleados_path,
            wraplength=500, justify="left")
        self.empleados_label.grid(row=1, column=1, sticky="ew", padx=10)

        # --- Panel de Resumen de Archivos ---
        summary_frame = ttk.LabelFrame(self, text=" 3. Resumen de Archivos ")
        summary_frame.grid(row=2, column=0, sticky="ew", pady=10)
        self.summary_text = tk.Label(summary_frame, text="Seleccione los archivos para ver el resumen.", justify="left")
        self.summary_text.pack(padx=10, pady=10, anchor="w")

        # --- Mapeo de Columnas ---
        self.mapping_frame = ttk.LabelFrame(
            self, text=" 2. Asigne las columnas del archivo de empleados ")
        self.mapping_frame.grid(row=3, column=0, sticky="ew", pady=10)
        self.mapping_frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(
            self.mapping_frame, text="Columna para NIF:"
        ).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.nif_combo = ttk.Combobox(
            self.mapping_frame,
            textvariable=self.controller.mapa_columnas["nif"],
            state="readonly")
        self.nif_combo.grid(row=0, column=1, sticky="ew", padx=10)

        tk.Label(
            self.mapping_frame, text="Columna para NOMBRE:"
        ).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.nombre_combo = ttk.Combobox(
            self.mapping_frame,
            textvariable=self.controller.mapa_columnas["nombre"],
            state="readonly")
        self.nombre_combo.grid(row=1, column=1, sticky="ew", padx=10)

        tk.Label(
            self.mapping_frame, text="Columna para EMAIL:"
        ).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.email_combo = ttk.Combobox(
            self.mapping_frame,
            textvariable=self.controller.mapa_columnas["email"],
            state="readonly")
        self.email_combo.grid(row=2, column=1, sticky="ew", padx=10)
        
        for combo in [self.nif_combo, self.nombre_combo, self.email_combo]:
            combo.bind("<<ComboboxSelected>>", self.verificar_estado)

        # --- Navegación ---
        nav_frame = tk.Frame(self)
        nav_frame.grid(row=4, column=0, sticky="se", pady=20)
        self.grid_rowconfigure(4, weight=1)  # Empuja el botón hacia abajo

        self.siguiente_btn = tk.Button(
            nav_frame, text="Siguiente →",
            command=self.ir_a_paso2, state="disabled")
        self.siguiente_btn.pack()
        
        self.actualizar_visibilidad_mapeo()

    def seleccionar_pdf(self):
        path = filedialog.askopenfilename(
            title="Seleccionar PDF Maestro",
            filetypes=[("Archivos PDF", "*.pdf")],
            initialdir=self.controller.last_dir
        )
        if path:
            self.controller.pdf_path.set(path)
            self.controller.last_dir = os.path.dirname(path)
            self.actualizar_resumen()
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
            self.actualizar_mapeo_columnas()
            self.actualizar_resumen()
            self.verificar_estado()

    def actualizar_mapeo_columnas(self):
        path = self.controller.empleados_path.get()
        if path:
            self.controller.columnas_disponibles = \
                leer_cabeceras_empleados(path)
            for combo in [self.nif_combo, self.nombre_combo, self.email_combo]:
                combo['values'] = self.controller.columnas_disponibles
        self.actualizar_visibilidad_mapeo()

    def actualizar_visibilidad_mapeo(self):
        if self.controller.empleados_path.get():
            self.mapping_frame.grid()
        else:
            self.mapping_frame.grid_remove()

    def actualizar_resumen(self):
        pdf_path = self.controller.pdf_path.get()
        empleados_path = self.controller.empleados_path.get()
        resumen = []
        
        if pdf_path:
            try:
                doc = fitz.open(pdf_path)
                resumen.append(f"📄 PDF: {doc.page_count} páginas encontradas.")
                doc.close()
            except Exception as e:
                resumen.append(f"📄 PDF: Error al leer - {e}")
        
        if empleados_path:
            try:
                df = leer_archivo_empleados(empleados_path)
                resumen.append(f"👥 Empleados: {len(df)} registros encontrados.")
            except Exception as e:
                resumen.append(f"👥 Empleados: Error al leer - {e}")
        
        if not resumen:
            resumen.append("Seleccione los archivos para ver el resumen.")
            
        self.summary_text.config(text="\n".join(resumen))

    def verificar_estado(self, event=None):
        pdf_ok = bool(self.controller.pdf_path.get())
        empleados_ok = bool(self.controller.empleados_path.get())
        mapa_ok = all(
            var.get() for var in self.controller.mapa_columnas.values())
        
        if pdf_ok and empleados_ok and mapa_ok:
            self.siguiente_btn.config(state="normal")
        else:
            self.siguiente_btn.config(state="disabled")

    def ir_a_paso2(self):
        mapa = {k: v.get() for k, v in self.controller.mapa_columnas.items()}
        res = analizar_archivos(
            self.controller.pdf_path.get(),
            self.controller.empleados_path.get(), mapa)
        
        if "error" in res:
            messagebox.showerror("Error de Análisis", res["error"])
            return
            
        self.controller.tareas_verificacion = res["tareas"]
        self.controller.frames["Paso2"].actualizar_tabla()
        self.controller.mostrar_frame("Paso2")


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
            show="headings")
        
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
            
            self.tree.insert("", "end", values=list(tarea.values()), tags=(row_style, status_tag))


class Paso3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        tk.Label(
            self, text="Paso 3: Envío de Correos",
            font=("Helvetica", 16, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")
        
        # --- Tabla de Envío ---
        tree_frame = tk.Frame(self)
        tree_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Nombre", "Email", "Protegido", "Estado", "Acción"),
            show="headings")
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        headings = {
            "Nombre": 200, "Email": 250, "Protegido": 100,
            "Estado": 150, "Acción": 100
        }
        for col, width in headings.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # --- Botones de Acción ---
        action_frame = tk.Frame(self)
        action_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        tk.Button(
            action_frame, text="← Anterior",
            command=lambda: controller.mostrar_frame("Paso2")
        ).pack(side="left")
        tk.Button(
            action_frame, text="Enviar a Todos",
            command=self.iniciar_envio_todos
        ).pack(side="right")

        self.controller.bind("<<ShowPaso3>>", self.actualizar_tabla_envio)

    def actualizar_tabla_envio(self, event=None):
        self.tree.delete(*self.tree.get_children())
        tareas_ok = [
            t for t in self.controller.tareas_verificacion
            if t['status'] == '✅ OK'
        ]
        for tarea in tareas_ok:
            self.tree.insert(
                "", "end",
                values=(
                    tarea["nombre"],
                    tarea["email"],
                    "✅",
                    "Pendiente",
                    "Enviar"
                )
            )

    def iniciar_envio_todos(self):
        email = self.controller.config.get('Email', 'email_origen', fallback='')
        password = self.controller.config.get('Email', 'password', fallback='')

        if not email or not password:
            messagebox.showwarning(
                "Ajustes incompletos",
                "Por favor, configure su email y contraseña en 'Ajustes'."
            )
            return

        if messagebox.askyesno(
            "Confirmar Envío",
            "¿Está seguro de que desea iniciar el envío de correos?"
        ):
            threading.Thread(
                target=enviar_nominas_worker,
                args=(
                    self.controller.pdf_path.get(),
                    self.controller.tareas_verificacion,
                    self.controller.config,
                    lambda msg: self.after(0, print, msg),  # Placeholder
                    lambda val: self.after(0, print, val)  # Placeholder
                ),
                daemon=True
            ).start()


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
        self.email_entry.insert(
            0, self.controller.config.get('Email', 'email_origen', fallback=''))

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


if __name__ == "__main__":
    app = AsistenteNominas()
    app.mainloop()
