import tkinter as tk
import platform


class SplashScreen(tk.Toplevel):
    """Professional splash screen with cross-platform compatibility.
    
    Displays application loading screen with proper window management
    for different window managers and operating systems.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Iniciando - Gestor de Nóminas")
        self.geometry("400x150")
        self.configure(bg="#f0f0f0")
        
        # Detect if environment supports window override (borderless windows)
        self.use_override = self._should_use_override()
        
        if self.use_override:
            self.overrideredirect(True)
        else:
            # En i3 y otros WM, usar ventana normal pero con configuraciones especiales
            self.resizable(False, False)
            self.attributes('-type', 'dialog')  # Hint para el WM
        
        # Center splash screen on screen
        self.center_window()
        
        # Create splash screen content
        self.create_content()
        
        # Force splash screen to appear in front
        self.lift()
        self.focus_force()
        
        # In i3 window manager, ensure visibility
        if not self.use_override:
            self.after(10, self.ensure_visible)
    
    def _should_use_override(self):
        """Detect if we can use window override redirect.
        
        Determines the best window display method based on operating system
        and window manager to ensure splash screen appears correctly.
        
        Returns:
            bool: True if override redirect should be used
        """
        import os
        
        # Windows: Always use override redirect for professional splash
        if platform.system() == 'Windows':
            return True
        
        # macOS: Override redirect works well
        if platform.system() == 'Darwin':
            return True
        
        # Linux: Detect problematic window managers
        try:
            wm_name = self.winfo_toplevel().wm_manager()
            if 'i3' in wm_name.lower():
                return False
        except:
            pass
        
        # Detect environment variables indicating problematic WMs
        if os.environ.get('DESKTOP_SESSION') == 'i3':
            return False
        if 'i3' in os.environ.get('XDG_SESSION_DESKTOP', '').lower():
            return False
            
        return True
    
    def center_window(self):
        """Center the splash window on screen.
        
        Calculates screen center position and positions splash window
        for optimal user experience during application startup.
        """
        self.update_idletasks()
        width = 400
        height = 150
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_content(self):
        """Create splash screen visual content.
        
        Sets up platform-appropriate styling, progress animation,
        and branding elements for professional appearance.
        """
        # Use native Windows styling when available
        if platform.system() == 'Windows':
            # Windows style with raised border
            main_frame = tk.Frame(self, bg="#f0f0f0", relief="raised", bd=2)
            title_font = ("Segoe UI", 14, "bold")
            subtitle_font = ("Segoe UI", 10)
        else:
            # Generic styling for other operating systems
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
        
        # Windows-style progress bar
        progress_frame = tk.Frame(main_frame, bg="#f0f0f0")
        progress_frame.pack(pady=(0, 20))
        
        # Windows: Use more native appearance
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
        
        # Start progress bar animation
        self.animate_progress()
    
    def animate_progress(self):
        """Animate the progress bar during application loading.
        
        Provides visual feedback to user while application components
        are being initialized in the background.
        """
        current_width = self.progress_fill.winfo_width()
        max_width = 320 if platform.system() == 'Windows' else 300
        
        if current_width < max_width:
            # Windows: Smoother animation timing
            increment = 15 if platform.system() == 'Windows' else 20
            new_width = min(max_width, current_width + increment)
            self.progress_fill.config(width=new_width)
            
            # Windows: Faster timing for better user experience
            delay = 80 if platform.system() == 'Windows' else 100
            self.after(delay, self.animate_progress)
    
    def ensure_visible(self):
        """Ensure splash window is visible in i3 window manager.
        
        i3 window manager requires special handling to ensure
        splash screens are displayed properly.
        """
        self.deiconify()
        self.lift()
        self.focus_force()
