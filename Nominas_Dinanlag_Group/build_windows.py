import PyInstaller.__main__
import os
import sys

# --- CONFIGURACIÓN ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NOMBRE_SCRIPT = "main.py"
CARPETA_APP = os.path.join(SCRIPT_DIR, "sistema_nominas")
NOMBRE_EXE = "EnviarNominas.exe"
CARPETA_DIST = os.path.join(SCRIPT_DIR, "dist_windows")

def construir_ejecutable_windows():
    """
    Crea ejecutable para Windows usando cross-compilation
    """
    print("--- Construyendo ejecutable para Windows ---")
    
    script_path = os.path.join(CARPETA_APP, NOMBRE_SCRIPT)
    
    if not os.path.exists(script_path):
        print(f"❌ Error: No se encuentra el script principal en '{script_path}'")
        return
    
    # Crear carpeta de destino
    os.makedirs(CARPETA_DIST, exist_ok=True)
    
    # Argumentos para PyInstaller con target Windows
    pyinstaller_args = [
        script_path,
        '--onefile',
        '--name', NOMBRE_EXE.replace('.exe', ''),
        '--clean',
        '--noconfirm',
        '--windowed',
        '--target-architecture', 'universal2',
        '--distpath', CARPETA_DIST,
    ]
    
    try:
        PyInstaller.__main__.run(pyinstaller_args)
        print("\n✅ Ejecutable Windows creado!")
        
        # Crear carpetas necesarias
        os.makedirs(os.path.join(CARPETA_DIST, "pdfs_entrada"), exist_ok=True)
        os.makedirs(os.path.join(CARPETA_DIST, "employee_data"), exist_ok=True)
        
        print(f"🎉 ¡Ejecutable listo en '{CARPETA_DIST}'!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    construir_ejecutable_windows()