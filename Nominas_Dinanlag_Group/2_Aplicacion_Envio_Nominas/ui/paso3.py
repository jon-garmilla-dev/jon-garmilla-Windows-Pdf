
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import queue
from logic.email_sender import enviar_nominas_worker


class Paso3(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.email_to_item_id = {}
        self.email_to_data = {}  # Almacenar datos originales
        self.update_queue = queue.Queue()

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
            columns=("Nombre", "Email", "Protegido", "Estado"),
            show="headings"
        )
        
        vsb = ttk.Scrollbar(
            tree_frame, orient="vertical", command=self.tree.yview
        )
        vsb.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")

        headings = {
            "Nombre": 200, "Email": 250, "Protegido": 100,
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
        
        tk.Button(
            action_frame, text="← Anterior",
            command=lambda: controller.mostrar_frame("Paso2")
        ).pack(side="left")
        self.send_all_button = tk.Button(
            action_frame, text="Enviar a Todos",
            command=self.iniciar_envio_todos
        )
        self.send_all_button.pack(side="right")

        self.controller.bind("<<ShowPaso3>>", self.actualizar_tabla_envio)

    def actualizar_tabla_envio(self, event=None):
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
            print(f"DEBUG UI: Fila {i+1} en tabla -> {tarea['nombre']} (página {tarea['pagina']})")
            item_id = self.tree.insert(
                "", "end",
                values=(
                    tarea["nombre"],
                    tarea["email"],
                    "✅",
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
            self.progress_bar['value'] = 0
            threading.Thread(
                target=enviar_nominas_worker,
                args=(
                    self.controller.pdf_path.get(),
                    self.controller.tareas_verificacion,
                    self.controller.config,
                    lambda email, msg, status: self.update_queue.put(
                        (email, msg, status)
                    ),
                    lambda val: self.after(0, self.update_progress, val),
                ),
                daemon=True
            ).start()
            self.after(100, self.procesar_cola_ui)

    def update_progress(self, value):
        if value == -1:
            self.send_all_button.config(state="normal")
            self.progress_bar['value'] = 100  # Finalizar la barra para terminar el bucle
            return
        self.progress_bar['value'] = value

    def procesar_cola_ui(self):
        try:
            while True:
                unique_key, msg, status = self.update_queue.get_nowait()
                item_id = self.email_to_item_id.get(unique_key)
                original_data = self.email_to_data.get(unique_key)
                if item_id and original_data:
                    print(f"DEBUG UPDATE: Actualizando {original_data[0]} -> {msg} ({status})")
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
