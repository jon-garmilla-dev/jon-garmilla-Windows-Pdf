import PyInstaller.__main__
import os

# --- CONFIGURACIÓN ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOMBRE_SCRIPT = "main.py"
CARPETA_APP = os.path.join(SCRIPT_DIR, "sistema_nominas")
NOMBRE_EXE = "GestorNominas.exe"
CARPETA_DIST = os.path.join(SCRIPT_DIR, "dist")


def construir_ejecutable():
    """
    Usa PyInstaller para empaquetar el script principal en un ejecutable.
    """
    print("--- Iniciando la construcción del ejecutable ---")
    
    # Ruta completa al script que queremos empaquetar
    script_path = os.path.join(CARPETA_APP, NOMBRE_SCRIPT)

    if not os.path.exists(script_path):
        print(
            f"❌ Error: No se encuentra el script principal en '{script_path}'")
        return

    # Argumentos para PyInstaller
    pyinstaller_args = [
        script_path,
        '--onefile',
        '--name', NOMBRE_EXE,
        '--clean',
        '--noconfirm',
        '--windowed',  # Para Windows GUI (sin consola)
    ]

    # Ejecutar PyInstaller
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n✅ PyInstaller ha finalizado con éxito.")
        
        # Mover las carpetas necesarias para que el .exe funcione
        print("--- Organizando la carpeta de distribución ---")
        
        # Crear las carpetas de datos dentro de la carpeta 'dist'
        os.makedirs(
            os.path.join(CARPETA_DIST, "pdfs_entrada"),
            exist_ok=True)
        os.makedirs(
            os.path.join(CARPETA_DIST, "2_nominas_individuales_encriptadas"),
            exist_ok=True)
        os.makedirs(
            os.path.join(CARPETA_DIST, "employee_data"),
            exist_ok=True)
        
        print("✅ Carpetas de datos creadas.")
        print(
            f"🎉 ¡Ejecutable creado! Lo encontrarás en la carpeta "
            f"'{CARPETA_DIST}'."
        )

    except Exception as e:
        print(f"❌ Error durante la ejecución de PyInstaller: {e}")


if __name__ == "__main__":
    construir_ejecutable()
