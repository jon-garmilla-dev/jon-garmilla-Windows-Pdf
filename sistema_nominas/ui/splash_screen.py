import tkinter as tk
import platform


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Iniciando - Gestor de Nóminas")
        self.geometry("400x150")
        self.configure(bg="#f0f0f0")
        
        # Detectar si estamos en un entorno que soporta overrideredirect
        self.use_override = self._should_use_override()
        
        if self.use_override:
            self.overrideredirect(True)
        else:
            # En i3 y otros WM, usar ventana normal pero con configuraciones especiales
            self.resizable(False, False)
            self.attributes('-type', 'dialog')  # Hint para el WM
        
        # Centrar en la pantalla
        self.center_window()
        
        # Crear contenido
        self.create_content()
        
        # Forzar que aparezca al frente
        self.lift()
        self.focus_force()
        
        # En i3, asegurar que se muestre
        if not self.use_override:
            self.after(10, self.ensure_visible)
    
    def _should_use_override(self):
        """Detecta si podemos usar overrideredirect"""
        import os
        
        # En Windows, usar siempre overrideredirect para splash profesional
        if platform.system() == 'Windows':
            return True
        
        # En macOS también funciona bien
        if platform.system() == 'Darwin':
            return True
        
        # En Linux, detectar window managers problemáticos
        try:
            wm_name = self.winfo_toplevel().wm_manager()
            if 'i3' in wm_name.lower():
                return False
        except:
            pass
        
        # Detectar variables de entorno que indican WM problemáticos
        if os.environ.get('DESKTOP_SESSION') == 'i3':
            return False
        if 'i3' in os.environ.get('XDG_SESSION_DESKTOP', '').lower():
            return False
            
        return True
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        width = 400
        height = 150
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_content(self):
        """Crea el contenido de la splash screen"""
        # Usar estilos nativos de Windows cuando sea posible
        if platform.system() == 'Windows':
            # Estilo Windows con borde raised
            main_frame = tk.Frame(self, bg="#f0f0f0", relief="raised", bd=2)
            title_font = ("Segoe UI", 14, "bold")
            subtitle_font = ("Segoe UI", 10)
        else:
            # Estilo genérico para otros OS
            main_frame = tk.Frame(self, bg="#f0f0f0", relief="ridge", bd=2)
            title_font = ("Arial", 14, "bold")
            subtitle_font = ("Arial", 10)
            
        main_frame.pack(fill="both", expand=True, padx=3, pady=3)

        tk.Label(
            main_frame, text="Gestor de Nóminas",
            font=title_font, bg="#f0f0f0", fg="#000080"
        ).pack(pady=(20, 8))
        
        tk.Label(
            main_frame, text="Iniciando aplicación...",
            font=subtitle_font, bg="#f0f0f0", fg="#606060"
        ).pack(pady=(0, 15))
        
        # Barra de progreso estilo Windows
        progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(pady=(0, 20))
        
        # En Windows, usar estilo más nativo
        if platform.system() == 'Windows':
            self.progress_bar = tk.Frame(progress_frame, bg="#ffffff", 
                                       relief="sunken", bd=1, height=8, width=320)
        else:
            self.progress_bar = tk.Frame(progress_frame, bg="#e0e0e0", 
                                       height=6, width=300)
        self.progress_bar.pack()
        
        self.progress_fill = tk.Frame(self.progress_bar, bg="#0066cc", 
                                    height=self.progress_bar['height'], width=0)
        self.progress_fill.place(x=0, y=0)
        
        # Iniciar animación de progreso
        self.animate_progress()
    
    def animate_progress(self):
        """Anima la barra de progreso"""
        current_width = self.progress_fill.winfo_width()
        max_width = 320 if platform.system() == 'Windows' else 300
        
        if current_width < max_width:
            # En Windows, animación más suave
            increment = 15 if platform.system() == 'Windows' else 20
            new_width = min(max_width, current_width + increment)
            self.progress_fill.config(width=new_width)
            
            # Timing más rápido en Windows
            delay = 80 if platform.system() == 'Windows' else 100
            self.after(delay, self.animate_progress)
    
    def ensure_visible(self):
        """Asegura que la ventana sea visible en i3"""
        self.deiconify()
        self.lift()
        self.focus_force()
