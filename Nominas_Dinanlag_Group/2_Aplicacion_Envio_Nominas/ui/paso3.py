
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
from datetime import datetime
from logic.email_sender import enviar_nominas_worker
from logic.formato_archivos import generar_nombre_archivo


class Paso3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.email_to_item_id = {}
        self.email_to_data = {}  # Almacenar datos originales
        self.update_queue = queue.Queue()
        
        # Estadísticas para el resumen final
        self.estadisticas = {"enviados": 0, "errores": 0, "total": 0, "tiempo_inicio": None}

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

        style = ttk.Style()
        style.map("Treeview",
                  background=[('selected', 'blue')],
                  foreground=[('selected', 'white')])
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Nombre", "Email", "Archivo PDF", "Estado"),
            show="headings"
        )
        
        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        headings = {
            "Nombre": 200, "Email": 250, "Archivo PDF": 300,
            "Estado": 150
        }
        for col, width in headings.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # --- Estilos de Filas y Tags ---
        self.tree.tag_configure('sent', background='#d4edda')
        self.tree.tag_configure('error', background='#f8d7da')
        self.tree.tag_configure('processing', background='#fff3cd')

        # --- Progress Bar ---
        progress_frame = ttk.Frame(self)
        progress_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        self.progress_bar = ttk.Progressbar(
            progress_frame, orient="horizontal", mode="determinate"
        )
        self.progress_bar.pack(fill="x", expand=True)

        # --- Botones de Acción ---
        action_frame = tk.Frame(self)
        action_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)
        
        self.btn_anterior = tk.Button(
            action_frame, text="← Anterior",
            command=self.ir_anterior,
            font=("MS Sans Serif", 8), width=12, height=2,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_anterior.pack(side="left")
        
        self.send_all_button = tk.Button(
            action_frame, text="Enviar a Todos",
            command=self.iniciar_envio_todos,
            font=("MS Sans Serif", 8, "bold"), width=15, height=2,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.send_all_button.pack(side="right")

        self.controller.bind("<<ShowPaso3>>", self.actualizar_tabla_envio)
        
        # Estado de envío para controlar navegación
        self.enviando = False

    def ir_anterior(self):
        """Navegar al paso anterior con validación."""
        if self.enviando:
            resultado = messagebox.askyesno(
                "Envío en Curso",
                "Hay un envío de nóminas en curso.\n\n"
                "Si regresa al paso anterior, el proceso se detendrá y "
                "podría perder el progreso actual.\n\n"
                "¿Está seguro de que desea continuar?",
                icon='warning'
            )
            if not resultado:
                return
            
            # Si acepta, detener proceso
            self.detener_envio()
        
        # Navegar al paso anterior
        self.controller.mostrar_frame("Paso2")
    
    def bloquear_navegacion(self):
        """Bloquea la navegación durante el envío."""
        self.enviando = True
        self.btn_anterior.config(
            state="disabled",
            text="← Enviando...",
            bg="#c0c0c0"
        )
    
    def desbloquear_navegacion(self):
        """Desbloquea la navegación después del envío."""
        self.enviando = False
        self.btn_anterior.config(
            state="normal",
            text="← Anterior", 
            bg="#e0e0e0"
        )
    
    def detener_envio(self):
        """Detiene el proceso de envío en curso."""
        # TODO: Implementar detención del hilo de envío
        self.desbloquear_navegacion()
        self.send_all_button.config(state="normal", text="Enviar a Todos")

    def actualizar_tabla_envio(self, event=None):
        """Actualiza la tabla y restablece el estado de navegación."""
        # Asegurar que navegación esté desbloqueada al entrar al paso
        self.desbloquear_navegacion()
        
        self.tree.delete(*self.tree.get_children())
        self.email_to_item_id = {}
        self.email_to_data = {}
        tareas_ok = [
            t for t in self.controller.tareas_verificacion
            if t['status'] == '✅ OK'
        ]
        # Ordenar por página para mostrar de arriba hacia abajo
        tareas_ok.sort(key=lambda x: x['pagina'])
        if not tareas_ok:
            self.send_all_button.config(state="disabled")
        else:
            self.send_all_button.config(state="normal")

        for i, tarea in enumerate(tareas_ok):
            # Generar nombre de archivo como se hará en el envío
            plantilla_archivo = self.controller.config.get('Formato', 'archivo_nomina', 
                                                          fallback='{nombre}_Nomina_{mes}_{año}.pdf')
            
            # Intentar obtener apellido si existe en la tarea, sino separar del nombre
            nombre = tarea['nombre']
            apellido_empleado = tarea.get('apellido', '')
            if not apellido_empleado and ' ' in nombre:
                partes = nombre.strip().split(' ', 1)
                nombre_empleado = partes[0]
                apellido_empleado = partes[1] if len(partes) > 1 else ''
            else:
                nombre_empleado = nombre
            
            nombre_archivo = generar_nombre_archivo(plantilla_archivo, nombre_empleado, apellido_empleado)
            
            item_id = self.tree.insert(
                "", "end",
                values=(
                    tarea["nombre"],
                    tarea["email"],
                    nombre_archivo,
                    "Pendiente"
                )
            )
            # Usar un mapeo único por página en lugar de email (que puede repetirse)
            unique_key = f"pagina_{tarea['pagina']}"
            self.email_to_item_id[unique_key] = item_id
            # Guardar los datos originales
            self.email_to_data[unique_key] = (tarea["nombre"], tarea["email"], "✅")

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
            # Inicializar estadísticas
            self.estadisticas = {
                "enviados": 0,
                "errores": 0, 
                "total": len([t for t in self.controller.tareas_verificacion if t['status'] == '✅ OK']),
                "tiempo_inicio": datetime.now()
            }
            
            self.progress_bar['value'] = 0
            self.send_all_button.config(state="disabled", text="Enviando...")
            self.bloquear_navegacion()  # Bloquear navegación durante envío
            
            threading.Thread(
                target=enviar_nominas_worker,
                args=(
                    self.controller.pdf_path.get(),
                    self.controller.tareas_verificacion,
                    self.controller.config,
                    lambda email, msg, status, stats=None: self.update_queue.put(
                        (email, msg, status, stats)
                    ),
                    lambda val: self.after(0, self.update_progress, val),
                ),
                daemon=True
            ).start()
            self.after(100, self.procesar_cola_ui)

    def update_progress(self, value):
        if value == -1:
            self.progress_bar['value'] = 100  # Finalizar la barra para terminar el bucle
            
            # Desbloquear navegación y restaurar botones
            self.desbloquear_navegacion()
            self.send_all_button.config(state="normal", text="Enviar a Todos")
            
            # Mostrar página de completado con estadísticas
            completado_frame = self.controller.frames["PasoCompletado"]
            completado_frame.actualizar_estadisticas(
                self.estadisticas["enviados"],
                self.estadisticas["errores"],
                self.estadisticas["total"],
                self.estadisticas["tiempo_inicio"]
            )
            
            # Cambiar a la página de completado
            self.after(1000, lambda: self.controller.mostrar_frame("PasoCompletado"))
            return
        self.progress_bar['value'] = value

    def procesar_cola_ui(self):
        try:
            while True:
                queue_item = self.update_queue.get_nowait()
                
                # Manejar formato con o sin estadísticas
                if len(queue_item) == 4:
                    unique_key, msg, status, stats = queue_item
                else:
                    unique_key, msg, status = queue_item
                    stats = None
                
                # Si recibimos estadísticas finales, usarlas en lugar del conteo manual
                if unique_key == "estadisticas_finales" and stats:
                    self.estadisticas["enviados"] = stats['enviados']
                    self.estadisticas["errores"] = stats['errores']
                    continue
                
                item_id = self.email_to_item_id.get(unique_key)
                original_data = self.email_to_data.get(unique_key)
                if item_id and original_data:
                    # Usar los datos originales almacenados, solo cambiar el estado
                    self.tree.item(
                        item_id,
                        values=(original_data[0], original_data[1], original_data[2], msg),
                        tags=(status,)
                    )
        except queue.Empty:
            pass
        finally:
            if self.progress_bar['value'] < 100:
                self.after(100, self.procesar_cola_ui)
