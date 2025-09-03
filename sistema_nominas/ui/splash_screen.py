import tkinter as tk


class SplashScreen(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Cargando")
        self.geometry("300x120")
        self.configure(bg="#f0f0f0")
        self.overrideredirect(True)  # Sin bordes de ventana

        # Centrar en la pantalla
        self.update_idletasks()
        width = 300
        height = 120
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

        main_frame = tk.Frame(self, bg="#f0f0f0", relief="solid", bd=1)
        main_frame.pack(fill="both", expand=True, padx=1, pady=1)

        tk.Label(
            main_frame, text="Gestor-De-Nominas-App",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0"
        ).pack(pady=(20, 5))
        
        tk.Label(
            main_frame, text="Iniciando, por favor espere...",
            font=("MS Sans Serif", 9), bg="#f0f0f0"
        ).pack(pady=(0, 20))

        self.lift()
