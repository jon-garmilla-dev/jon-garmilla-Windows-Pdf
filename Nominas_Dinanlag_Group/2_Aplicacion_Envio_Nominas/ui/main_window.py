import tkinter as tk
import os
from logic.settings import load_settings
from ui.paso1 import Paso1
from ui.paso2 import Paso2
from ui.paso3 import Paso3
from ui.paso_ajustes import PasoAjustes
from ui.paso_completado import PasoCompletado


class AsistenteNominas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Asistente de Envío de Nóminas v2.0")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(bg="#f0f0f0")  # Fondo gris claro estilo Windows
        
        self.config = load_settings()

        # Variables de estado compartidas
        self.pdf_path = tk.StringVar()
        self.empleados_path = tk.StringVar()
        self.last_dir = os.path.expanduser("~")
        self.columnas_disponibles = []
        self.mapa_columnas = {
            "nif": tk.StringVar(),
            "nombre": tk.StringVar(),
            "apellidos": tk.StringVar(),
            "email": tk.StringVar()
        }
        self.tareas_verificacion = []

        self._crear_widgets()
        self.mostrar_frame("Paso1")

    def _crear_widgets(self):
        # Contenedor principal con estilo Windows
        main_frame = tk.Frame(self, bg="#f0f0f0", relief="flat")
        main_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Panel lateral estilo Windows con borde
        panel_lateral = tk.Frame(main_frame, bg="#e8e8e8", width=220, relief="ridge", bd=2)
        panel_lateral.pack(side="left", fill="y", padx=(0, 8))

        # Título del panel con estilo Windows
        titulo_frame = tk.Frame(panel_lateral, bg="#d4d0c8", relief="ridge", bd=1)
        titulo_frame.pack(fill="x", padx=4, pady=4)
        
        tk.Label(
            titulo_frame, text="Pasos del Proceso",
            font=("MS Sans Serif", 9, "bold"), bg="#d4d0c8", fg="#000000"
        ).pack(pady=6)
        # Botones de pasos estilo Windows clásico
        self.pasos_labels = {
            "Paso1": tk.Label(
                panel_lateral, text="1. Selección de Archivos", bg="#e8e8e8",
                anchor="w", font=("MS Sans Serif", 9), fg="#000000", 
                relief="flat", padx=12, pady=6),
            "Paso2": tk.Label(
                panel_lateral, text="2. Verificación de Datos", bg="#e8e8e8",
                anchor="w", font=("MS Sans Serif", 9), fg="#000000",
                relief="flat", padx=12, pady=6),
            "Paso3": tk.Label(
                panel_lateral, text="3. Envío de Correos", bg="#e8e8e8",
                anchor="w", font=("MS Sans Serif", 9), fg="#000000",
                relief="flat", padx=12, pady=6),
            "PasoAjustes": tk.Label(
                panel_lateral, text="Configuración", bg="#e8e8e8",
                anchor="w", font=("MS Sans Serif", 9), fg="#000000",
                relief="flat", padx=12, pady=6)
        }
        
        # Separador entre pasos normales y configuración
        separador = tk.Frame(panel_lateral, height=2, bg="#c0c0c0", relief="sunken", bd=1)
        
        # Layout de los pasos y el botón de ajustes con estilo Windows
        for name, label in self.pasos_labels.items():
            if name == "PasoAjustes":
                separador.pack(fill="x", padx=8, pady=(10, 5))
                label.pack(fill="x", padx=8, pady=(5, 10))
            else:
                label.pack(fill="x", padx=8, pady=2)
            
            # Eventos con efectos visuales estilo Windows
            label.bind(
                "<Button-1>",
                lambda e, page_name=name: self.mostrar_frame(page_name)
            )
            label.bind("<Enter>", lambda e: self._on_hover_enter(e.widget))
            label.bind("<Leave>", lambda e: self._on_hover_leave(e.widget))

        # Contenedor para los pasos (frames) con borde estilo Windows
        container_frame = tk.Frame(main_frame, bg="#f0f0f0", relief="ridge", bd=2)
        container_frame.pack(side="right", fill="both", expand=True)
        
        self.container = tk.Frame(container_frame, bg="#f0f0f0")
        self.container.pack(fill="both", expand=True, padx=8, pady=8)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (Paso1, Paso2, Paso3, PasoAjustes, PasoCompletado):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

    def _on_hover_enter(self, widget):
        """Efecto hover estilo Windows - entrada del mouse"""
        current_bg = widget.cget("bg")
        if current_bg != "#316ac5":  # Si no está seleccionado
            widget.config(bg="#b8cde8", cursor="hand2")

    def _on_hover_leave(self, widget):
        """Efecto hover estilo Windows - salida del mouse"""
        current_bg = widget.cget("bg")
        if current_bg != "#316ac5":  # Si no está seleccionado
            widget.config(bg="#e8e8e8", cursor="")

    def mostrar_frame(self, page_name):
        """Muestra un frame y resalta el paso actual con estilo Windows."""
        # Validar si se puede acceder al paso
        if not self._puede_acceder_paso(page_name):
            return
            
        if page_name == "Paso3":
            self.event_generate("<<ShowPaso3>>")

        for name, label in self.pasos_labels.items():
            is_active = (name == page_name)
            if is_active:
                # Estilo seleccionado estilo Windows
                label.config(font=("MS Sans Serif", 9, "bold"), bg="#316ac5", fg="#ffffff")
            else:
                # Estilo normal
                label.config(font=("MS Sans Serif", 9, "normal"), bg="#e8e8e8", fg="#000000")
        
        frame = self.frames[page_name]
        frame.tkraise()
    
    def bloquear_navegacion_lateral(self):
        """Bloquea la navegación del panel lateral durante envío."""
        for name, label in self.pasos_labels.items():
            label.config(
                state="disabled",
                fg="#808080",  # Gris desactivado
                cursor=""
            )
            # Desenlazar eventos de clic temporalmente
            label.unbind("<Button-1>")
            label.unbind("<Enter>")
            label.unbind("<Leave>")
    
    def desbloquear_navegacion_lateral(self):
        """Desbloquea la navegación del panel lateral después del envío."""
        for name, label in self.pasos_labels.items():
            label.config(
                state="normal",
                fg="#000000",  # Negro normal
                cursor="hand2"
            )
            # Reenlazar eventos de clic
            label.bind(
                "<Button-1>",
                lambda e, page_name=name: self.mostrar_frame(page_name)
            )
            label.bind("<Enter>", lambda e: self._on_hover_enter(e.widget))
            label.bind("<Leave>", lambda e: self._on_hover_leave(e.widget))
        
    def _puede_acceder_paso(self, page_name):
        """Valida si se puede acceder al paso solicitado"""
        if page_name in ["Paso1", "PasoAjustes"]:
            return True
            
        # Para paso 2: necesita PDF y empleados seleccionados
        if page_name == "Paso2":
            if not self.pdf_path.get() or not self.empleados_path.get():
                from tkinter import messagebox
                messagebox.showwarning(
                    "Paso Incompleto",
                    "Debe completar la selección de archivos en el Paso 1\n"
                    "antes de continuar a la verificación de datos."
                )
                return False
            # También verificar que las columnas estén mapeadas (apellidos es opcional)
            campos_requeridos = ["nif", "nombre", "email"]
            campos_faltantes = []
            for campo in campos_requeridos:
                if not self.mapa_columnas[campo].get():
                    campos_faltantes.append(campo.upper())
            
            if campos_faltantes:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Configuración Incompleta", 
                    f"Debe asignar estas columnas en el Paso 1:\n{', '.join(campos_faltantes)}\n\n"
                    "Nota: APELLIDOS es opcional"
                )
                return False
        
        # Para paso 3: necesita verificación completada
        if page_name == "Paso3":
            if not hasattr(self, 'tareas_verificacion') or not self.tareas_verificacion:
                from tkinter import messagebox
                messagebox.showwarning(
                    "Verificación Incompleta",
                    "Debe completar la verificación de datos en el Paso 2\n"
                    "antes de continuar al envío de correos."
                )
                return False
                
        return True

    def abrir_ajustes(self):
        self.mostrar_frame("PasoAjustes")
