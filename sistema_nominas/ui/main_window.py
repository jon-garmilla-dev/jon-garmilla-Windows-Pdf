import tkinter as tk
import os
from logic.settings import load_settings
from ui.paso1 import Paso1
from ui.paso2 import Paso2
from ui.paso3 import Paso3
from ui.paso_ajustes import PasoAjustes
from ui.paso_completado import PasoCompletado


class GestorNominasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # Ocultar la ventana principal al inicio
        self.title("Gestor-De-Nominas-App")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.configure(bg="#f0f0f0")  # Fondo gris claro estilo Windows
        
        # Centrar la ventana en la pantalla
        self.center_window()
        
        # Mostrar splash screen
        self._show_splash()
        
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
        
        # Control de navegación secuencial
        self.paso_actual = "Paso1"

        self._crear_widgets()
        self.mostrar_frame("Paso1", forzar=True)  # Forzar mostrar Paso1 al inicio
        # Asegurar estilos correctos al inicio
        self._actualizar_estilos_pasos()

        # Manejar el cierre de la ventana
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Ocultar splash cuando la app esté completamente cargada
        self.after_idle(self._hide_splash_show_main)
        
    def ir_a_paso_siguiente(self, destino):
        """Navega al paso siguiente usando los botones Siguiente/Anterior."""
        # Permitir navegación por botones independientemente de las reglas del panel lateral
        self.paso_actual = destino
        self._actualizar_estilos_pasos()
        
        if destino == "Paso3":
            self.event_generate("<<ShowPaso3>>")
        
        frame = self.frames[destino]
        frame.tkraise()

    def center_window(self):
        """Centra la ventana en la pantalla principal."""
        self.update_idletasks()
        width = 1200
        height = 800
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def _show_splash(self):
        """Muestra la splash screen."""
        import time
        from ui.splash_screen import SplashScreen
        
        # Marcar inicio del splash para timing
        self._splash_start_time = time.time()
        
        self.splash = SplashScreen(self)
        self.splash.transient(self)  # Hace que la splash sea hija de la ventana principal
        self.splash.grab_set()  # Hace que la splash sea modal
    
    def _hide_splash_show_main(self):
        """Oculta la splash screen y muestra la ventana principal."""
        import time
        
        # Calcular tiempo transcurrido desde inicio
        if not hasattr(self, '_splash_start_time'):
            self._splash_start_time = time.time()
        
        elapsed_time = time.time() - self._splash_start_time
        
        # Tiempo mínimo para que se vea el splash (1 segundo)  
        min_splash_time = 1.0
        
        if elapsed_time < min_splash_time:
            # Esperar el tiempo necesario para completar el tiempo mínimo
            remaining_time = int((min_splash_time - elapsed_time) * 1000)
            self.after(remaining_time, self._actually_hide_splash)
        else:
            # Ya pasó suficiente tiempo, mostrar inmediatamente
            self._actually_hide_splash()
    
    def _actually_hide_splash(self):
        """Realmente oculta la splash y muestra la ventana principal."""
        if hasattr(self, 'splash'):
            self.splash.destroy()
        self.deiconify()
    
    def center_dialog(self, dialog_window):
        """Centra un diálogo sobre la ventana principal."""
        dialog_window.transient(self)
        dialog_window.grab_set()
        self.update_idletasks()
        dialog_window.update_idletasks()
        
        # Obtener dimensiones de la ventana principal
        main_x = self.winfo_x()
        main_y = self.winfo_y()
        main_width = self.winfo_width()
        main_height = self.winfo_height()
        
        # Obtener dimensiones del diálogo
        dialog_width = dialog_window.winfo_width()
        dialog_height = dialog_window.winfo_height()
        
        # Calcular posición centrada
        x = main_x + (main_width // 2) - (dialog_width // 2)
        y = main_y + (main_height // 2) - (dialog_height // 2)
        
        dialog_window.geometry(f'+{x}+{y}')
    
    def show_centered_messagebox(self, msg_type, title, message, **kwargs):
        """Muestra un messagebox centrado sobre la ventana principal."""
        from tkinter import messagebox
        # Asegurar que el parent sea esta ventana
        kwargs['parent'] = self
        
        if msg_type == 'info':
            return messagebox.showinfo(title, message, **kwargs)
        elif msg_type == 'warning':
            return messagebox.showwarning(title, message, **kwargs)
        elif msg_type == 'error':
            return messagebox.showerror(title, message, **kwargs)
        elif msg_type == 'yesno':
            return messagebox.askyesno(title, message, **kwargs)
        elif msg_type == 'okcancel':
            return messagebox.askokcancel(title, message, **kwargs)
    
    def show_centered_filedialog(self, dialog_type, **kwargs):
        """Muestra un filedialog centrado sobre la ventana principal."""
        from tkinter import filedialog
        # Asegurar que el parent sea esta ventana
        kwargs['parent'] = self
        
        if dialog_type == 'openfilename':
            return filedialog.askopenfilename(**kwargs)
        elif dialog_type == 'saveasfilename':
            return filedialog.asksaveasfilename(**kwargs)
        elif dialog_type == 'askdirectory':
            return filedialog.askdirectory(**kwargs)
    
    def _on_closing(self):
        """Maneja el evento de cierre de la ventana."""
        self.destroy()

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
                panel_lateral, text="1. Selección de Archivos",
                bg="#e8e8e8", anchor="w", font=("MS Sans Serif", 9),
                fg="#000000", relief="flat", padx=12, pady=6),
            "Paso2": tk.Label(
                panel_lateral, text="2. Verificación de Datos",
                bg="#e8e8e8", anchor="w", font=("MS Sans Serif", 9),
                fg="#000000", relief="flat", padx=12, pady=6),
            "Paso3": tk.Label(
                panel_lateral, text="3. Envío de Correos",
                bg="#e8e8e8", anchor="w", font=("MS Sans Serif", 9),
                fg="#000000", relief="flat", padx=12, pady=6),
            "PasoAjustes": tk.Label(
                panel_lateral, text="Configuración",
                bg="#e8e8e8", anchor="w", font=("MS Sans Serif", 9),
                fg="#000000", relief="flat", padx=12, pady=6)
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

        container_frame = tk.Frame(
            main_frame, bg="#f0f0f0", relief="ridge", bd=2)
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

    def mostrar_frame(self, page_name, forzar=False):
        """Muestra un frame y resalta el paso actual con estilo Windows."""
        # Validar navegación secuencial estricta (excepto si se fuerza)
        if not forzar and not self._puede_navegar_a_paso(page_name):
            return
        
        # Actualizar paso actual
        self.paso_actual = page_name
            
        if page_name == "Paso3":
            self.event_generate("<<ShowPaso3>>")

        # Actualizar estilos visuales de todos los pasos
        self._actualizar_estilos_pasos()
        
        frame = self.frames[page_name]
        frame.tkraise()
    
    def _puede_navegar_a_paso(self, destino):
        """Determina si se puede navegar al paso destino según las reglas de seguridad."""
        actual = self.paso_actual
        
        # NO permitir hacer clic en el mismo paso - es redundante
        if actual == destino:
            return False
            
        # Reglas de navegación secuencial estricta:
        if actual == "Paso1":
            # Desde Paso1 solo puedes ir a PasoAjustes, no a ti mismo
            return destino in ["PasoAjustes"]
            
        elif actual == "Paso2":
            # Desde Paso2 solo puedes ir a Paso1 (atrás)
            return destino in ["Paso1"]
            
        elif actual == "Paso3":
            # Desde Paso3 solo puedes ir a Paso2 (atrás)
            return destino in ["Paso2"]
            
        elif actual == "PasoAjustes":
            # Desde Configuración solo puedes volver a Paso1
            return destino in ["Paso1"]
            
        elif actual == "PasoCompletado":
            # Desde Completado puedes ir a cualquier lado (reiniciar proceso)
            return True
            
        return False
    
    def _actualizar_estilos_pasos(self):
        """Actualiza los estilos visuales de todos los pasos según el estado actual."""
        for name, label in self.pasos_labels.items():
            puede_navegar = self._puede_navegar_a_paso(name)
            is_active = (name == self.paso_actual)
            
            if is_active:
                # Paso actual - azul activo
                label.config(
                    font=("MS Sans Serif", 9, "bold"),
                    bg="#316ac5", fg="#ffffff",
                    cursor="hand2")
            elif puede_navegar:
                # Pasos accesibles - normal
                label.config(
                    font=("MS Sans Serif", 9, "normal"),
                    bg="#e8e8e8", fg="#000000",
                    cursor="hand2")
            else:
                # Pasos bloqueados - gris deshabilitado
                label.config(
                    font=("MS Sans Serif", 9, "normal"),
                    bg="#e8e8e8", fg="#808080",
                    cursor="")
    
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
                self.show_centered_messagebox(
                    "warning",
                    "Paso Incompleto",
                    "Debe completar la selección de archivos en el Paso 1\n"
                    "antes de continuar a la verificación de datos.")
                return False
            # También verificar que las columnas estén mapeadas (todos los campos son obligatorios)
            campos_requeridos = ["nif", "nombre", "apellidos", "email"]
            campos_faltantes = []
            for campo in campos_requeridos:
                if not self.mapa_columnas[campo].get():
                    campos_faltantes.append(campo.upper())
            
            if campos_faltantes:
                from tkinter import messagebox
                self.show_centered_messagebox(
                    "warning",
                    "Configuración Incompleta",
                    f"Debe asignar estas columnas en el Paso 1:\n"
                    f"{', '.join(campos_faltantes)}\n\n"
                    "Todos los campos son obligatorios.")
                return False
        
        if page_name == "Paso3":
            if not hasattr(self, 'tareas_verificacion') or \
               not self.tareas_verificacion:
                from tkinter import messagebox
                self.show_centered_messagebox(
                    "warning",
                    "Verificación Incompleta",
                    "Debe completar la verificación de datos en el Paso 2\n"
                    "antes de continuar al envío de correos.")
                return False
                
        return True

    def abrir_ajustes(self):
        self.mostrar_frame("PasoAjustes")
        
    def guardar_configuracion(self):
        """Guarda la configuración actual en el archivo settings.ini"""
        try:
            from logic.settings import save_settings
            save_settings(self.config)
        except Exception as e:
            print(f"Error guardando configuración: {e}")
