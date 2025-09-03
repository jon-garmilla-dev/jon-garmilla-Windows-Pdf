import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import os


class PasoCompletado(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#f0f0f0")
        self.controller = controller
        self.estadisticas = {"enviados": 0, "errores": 0, "total": 0, "tiempo_inicio": None}

        # Título principal estilo Windows
        titulo_frame = tk.Frame(self, bg="#f0f0f0")
        titulo_frame.pack(fill="x", pady=(0, 20))
        
        # Ícono de éxito (simulado con texto)
        icono_frame = tk.Frame(titulo_frame, bg="#f0f0f0")
        icono_frame.pack()
        
        tk.Label(
            icono_frame, text="✓",
            font=("MS Sans Serif", 48, "bold"), bg="#f0f0f0", fg="#008000"
        ).pack()
        
        tk.Label(
            titulo_frame, text="Proceso de Envío Completado",
            font=("MS Sans Serif", 16, "bold"), bg="#f0f0f0", fg="#000000"
        ).pack(pady=(10, 5))
        
        self.subtitulo_label = tk.Label(
            titulo_frame, text="El proceso ha finalizado correctamente.",
            font=("MS Sans Serif", 10), bg="#f0f0f0", fg="#404040"
        )
        self.subtitulo_label.pack()

        # Resumen estadístico estilo Windows
        stats_frame = tk.LabelFrame(
            self, text=" Resumen del Proceso ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        stats_frame.pack(fill="x", expand=False, pady=(0, 20))
        stats_frame.configure(bg="#f0f0f0")

        # Grid de estadísticas
        stats_grid = tk.Frame(stats_frame, bg="#f0f0f0")
        stats_grid.pack(fill="x", padx=20, pady=15)

        # Columna izquierda
        left_column = tk.Frame(stats_grid, bg="#f0f0f0")
        left_column.pack(side="left", fill="both", expand=True)

        tk.Label(
            left_column, text="Correos enviados exitosamente:",
            font=("MS Sans Serif", 9), bg="#f0f0f0", fg="#000000", anchor="w"
        ).pack(fill="x", pady=2)
        
        self.enviados_label = tk.Label(
            left_column, text="0",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0", fg="#008000", anchor="w"
        )
        self.enviados_label.pack(fill="x", pady=(0, 10))

        tk.Label(
            left_column, text="Errores encontrados:",
            font=("MS Sans Serif", 9), bg="#f0f0f0", fg="#000000", anchor="w"
        ).pack(fill="x", pady=2)
        
        self.errores_label = tk.Label(
            left_column, text="0",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0", fg="#800000", anchor="w"
        )
        self.errores_label.pack(fill="x")

        # Columna derecha
        right_column = tk.Frame(stats_grid, bg="#f0f0f0")
        right_column.pack(side="right", fill="both", expand=True)

        tk.Label(
            right_column, text="Total procesado:",
            font=("MS Sans Serif", 9), bg="#f0f0f0", fg="#000000", anchor="w"
        ).pack(fill="x", pady=2)
        
        self.total_label = tk.Label(
            right_column, text="0",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0", fg="#000080", anchor="w"
        )
        self.total_label.pack(fill="x", pady=(0, 10))

        tk.Label(
            right_column, text="Tiempo transcurrido:",
            font=("MS Sans Serif", 9), bg="#f0f0f0", fg="#000000", anchor="w"
        ).pack(fill="x", pady=2)
        
        self.tiempo_label = tk.Label(
            right_column, text="--:--",
            font=("MS Sans Serif", 12, "bold"), bg="#f0f0f0", fg="#000080", anchor="w"
        )
        self.tiempo_label.pack(fill="x")

        # Información adicional estilo Windows
        info_frame = tk.LabelFrame(
            self, text=" Información Adicional ",
            font=("MS Sans Serif", 8, "bold"), bg="#f0f0f0", fg="#000000",
            relief="groove", bd=2
        )
        info_frame.pack(fill="x", expand=False, pady=(0, 20))
        info_frame.configure(bg="#f0f0f0")

        self.info_label = tk.Label(
            info_frame, text="Los archivos PDF individuales se han guardado en la carpeta configurada.",
            font=("MS Sans Serif", 9), bg="#f0f0f0", fg="#404040",
            justify="left", anchor="w", wraplength=600
        )
        self.info_label.pack(fill="x", padx=15, pady=10)

        # Botones de acción estilo Windows
        btn_frame = tk.Frame(self, bg="#f0f0f0")
        btn_frame.pack(side="bottom", fill="x", pady=(10, 0))
        
        # Separador estilo Windows
        separator = tk.Frame(btn_frame, height=1, bg="#c0c0c0", relief="sunken", bd=1)
        separator.pack(fill="x", pady=(0, 15))
        
        buttons_container = tk.Frame(btn_frame, bg="#f0f0f0")
        buttons_container.pack(side="right")
        
        self.btn_carpeta = tk.Button(
            buttons_container, text="Abrir Carpeta",
            font=("MS Sans Serif", 8), width=15, height=2,
            command=self.abrir_carpeta_salida,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_carpeta.pack(side="left", padx=(0, 8))
        
        self.btn_nuevo = tk.Button(
            buttons_container, text="Nuevo Proceso",
            font=("MS Sans Serif", 8, "bold"), width=15, height=2,
            command=self.iniciar_nuevo_proceso,
            relief="raised", bd=2, bg="#e0e0e0"
        )
        self.btn_nuevo.pack(side="left")

    def actualizar_estadisticas(self, enviados, errores, total, tiempo_inicio, stats_extra=None):
        """Actualiza las estadísticas mostradas"""
        self.estadisticas = {
            "enviados": enviados,
            "errores": errores, 
            "total": total,
            "tiempo_inicio": tiempo_inicio
        }
        
        # Guardar estadísticas extra (rutas de carpetas y reportes)
        self.stats_extra = stats_extra or {}
        
        self.enviados_label.config(text=str(enviados))
        self.errores_label.config(text=str(errores))
        self.total_label.config(text=str(total))
        
        # Calcular tiempo transcurrido
        if tiempo_inicio:
            tiempo_transcurrido = datetime.now() - tiempo_inicio
            minutos = int(tiempo_transcurrido.total_seconds() // 60)
            segundos = int(tiempo_transcurrido.total_seconds() % 60)
            self.tiempo_label.config(text=f"{minutos:02d}:{segundos:02d}")
        
        # Actualizar subtítulo basado en resultados
        if errores == 0:
            self.subtitulo_label.config(
                text="Todos los correos se enviaron correctamente.",
                fg="#008000"
            )
        elif enviados == 0:
            self.subtitulo_label.config(
                text="No se pudo enviar ningún correo. Revise la configuración.",
                fg="#800000"
            )
        else:
            self.subtitulo_label.config(
                text=f"Se enviaron {enviados} de {total} correos correctamente.",
                fg="#804000"
            )
        
        # Actualizar información adicional con estructura organizada
        carpeta_mes = self.stats_extra.get('carpeta_mes')
        carpeta_pdfs = self.stats_extra.get('carpeta_pdfs')
        archivo_reporte = self.stats_extra.get('archivo_reporte_excel')
        
        if carpeta_mes and carpeta_pdfs:
            # Mostrar nueva estructura organizada
            info_text = f"Proceso completado exitosamente\n\n"
            info_text += f"Carpeta del mes: {os.path.basename(carpeta_mes)}\n"
            info_text += f"PDFs individuales: /pdfs_individuales/\n"
            if archivo_reporte:
                info_text += f"Reporte Excel: {os.path.basename(archivo_reporte)}\n"
            info_text += f"Resumen TXT generado automaticamente"
        else:
            # Fallback a comportamiento anterior
            carpeta_salida = self.controller.config.get('Carpetas', 'salida', fallback='nominas_individuales')
            carpeta_display = carpeta_salida.replace('/', '\\') if '/' in carpeta_salida else carpeta_salida
            if not carpeta_display.startswith('\\') and ':' not in carpeta_display:
                carpeta_display = f"📁 {carpeta_display}"
            info_text = f"Los archivos PDF individuales se han guardado en:\n{carpeta_display}"
        
        self.info_label.config(text=info_text)

    def abrir_carpeta_salida(self):
        """Abre la carpeta donde se guardaron los PDFs"""
        # Priorizar la carpeta del mes si existe
        carpeta_abrir = getattr(self, 'stats_extra', {}).get('carpeta_mes')
        
        if not carpeta_abrir:
            # Fallback a configuración anterior
            carpeta_abrir = self.controller.config.get('Carpetas', 'salida', fallback='nominas_individuales')
        
        try:
            if os.path.exists(carpeta_abrir):
                # Intentar abrir con el explorador del sistema
                import subprocess
                import sys
                
                if sys.platform == "win32":
                    os.startfile(carpeta_abrir)
                elif sys.platform == "darwin":
                    subprocess.Popen(["open", carpeta_abrir])
                else:
                    subprocess.Popen(["xdg-open", carpeta_abrir])
                    
                print(f"Abriendo carpeta: {carpeta_abrir}")
            else:
                messagebox.showwarning(
                    "Carpeta no encontrada",
                    f"La carpeta no existe:\n{carpeta_abrir}"
                )
        except Exception as e:
            messagebox.showerror(
                "Error al abrir carpeta",
                f"No se pudo abrir la carpeta:\n{e}"
            )

    def iniciar_nuevo_proceso(self):
        """Regresa al paso 1 para un nuevo proceso"""
        # Limpiar datos del proceso anterior
        self.controller.pdf_path.set("")
        self.controller.empleados_path.set("")
        self.controller.tareas_verificacion = []
        
        # Limpiar mapeo de columnas
        for var in self.controller.mapa_columnas.values():
            var.set("")
        
        # Mostrar paso 1
        self.controller.mostrar_frame("Paso1")
        
        messagebox.showinfo(
            "Nuevo Proceso",
            "Puede comenzar un nuevo proceso de envío de nóminas."
        )