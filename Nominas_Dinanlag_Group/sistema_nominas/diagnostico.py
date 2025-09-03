#!/usr/bin/env python3
"""
Script de diagnóstico para la aplicación de envío de nóminas
Ayuda a identificar problemas comunes en diferentes sistemas
"""

import sys
import os
import subprocess
import platform

def check_python_version():
    """Verifica la versión de Python"""
    print(f"🐍 Python: {sys.version}")
    if sys.version_info < (3, 9):
        print("⚠️  ADVERTENCIA: Se recomienda Python 3.9 o superior")
    else:
        print("✅ Versión de Python OK")

def check_system_info():
    """Información del sistema"""
    print(f"💻 Sistema: {platform.system()} {platform.release()}")
    print(f"🏗️  Arquitectura: {platform.machine()}")
    print(f"🔧 Plataforma: {sys.platform}")

def check_tkinter():
    """Verifica tkinter"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # No mostrar ventana
        root.destroy()
        print("✅ tkinter: Disponible y funcional")
    except Exception as e:
        print(f"❌ tkinter: Error - {e}")
        if sys.platform.startswith('linux'):
            print("💡 Intente: sudo apt-get install python3-tk")

def check_pil():
    """Verifica PIL/Pillow"""
    try:
        from PIL import Image, ImageTk
        print("✅ PIL/Pillow: Disponible")
        
        # Probar crear imagen simple
        img = Image.new('RGB', (100, 100), color='red')
        print("✅ PIL: Creación de imágenes OK")
        
        # Probar ImageTk
        photo = ImageTk.PhotoImage(img)
        print("✅ ImageTk: Conversión para tkinter OK")
        
    except ImportError as e:
        print(f"❌ PIL/Pillow: No instalado - {e}")
        if sys.platform.startswith('linux'):
            print("💡 Intente: sudo apt-get install python3-pil python3-pil.imagetk")
            print("💡 O: pip install Pillow")
    except Exception as e:
        print(f"⚠️  PIL/Pillow: Instalado pero con errores - {e}")

def check_pdf_libraries():
    """Verifica librerías de PDF"""
    try:
        import fitz
        print(f"✅ PyMuPDF: {fitz.version[0]} disponible")
    except ImportError:
        print("❌ PyMuPDF: No instalado")
        print("💡 Intente: pip install pymupdf")
    
    try:
        import pikepdf
        print("✅ pikepdf: Disponible para encriptación")
    except ImportError:
        print("❌ pikepdf: No instalado")
        print("💡 Intente: pip install pikepdf")

def check_pdf_viewers():
    """Verifica visores de PDF disponibles"""
    if sys.platform == "win32":
        print("🖥️  Windows: Usando asociaciones de archivo del sistema")
    elif sys.platform == "darwin":
        print("🍎 macOS: Usando 'open' del sistema")
    else:
        print("🐧 Linux: Verificando visores de PDF...")
        viewers = ['xdg-open', 'evince', 'okular', 'zathura', 'mupdf', 'firefox']
        found_viewers = []
        
        for viewer in viewers:
            try:
                result = subprocess.run(['which', viewer], capture_output=True, text=True)
                if result.returncode == 0:
                    found_viewers.append(viewer)
            except:
                pass
        
        if found_viewers:
            print(f"✅ Visores encontrados: {', '.join(found_viewers)}")
        else:
            print("❌ No se encontraron visores de PDF")
            print("💡 Instale uno: sudo apt-get install evince")

def check_shell_environment():
    """Verifica el entorno de shell"""
    try:
        result = subprocess.run(['echo', 'test'], capture_output=True, text=True, timeout=2)
        if result.returncode == 0:
            print("✅ Subprocess: Funcionando correctamente")
        else:
            print("⚠️  Subprocess: Problemas detectados")
    except Exception as e:
        print(f"❌ Subprocess: Error - {e}")

def main():
    print("=" * 60)
    print("🔧 DIAGNÓSTICO - Asistente de Envío de Nóminas")
    print("=" * 60)
    print()
    
    print("📋 INFORMACIÓN DEL SISTEMA")
    print("-" * 30)
    check_python_version()
    check_system_info()
    print()
    
    print("📚 LIBRERÍAS PRINCIPALES")  
    print("-" * 30)
    check_tkinter()
    check_pil()
    check_pdf_libraries()
    print()
    
    print("🖥️  FUNCIONALIDADES EXTERNAS")
    print("-" * 30)
    check_pdf_viewers()
    check_shell_environment()
    print()
    
    print("📝 RECOMENDACIONES")
    print("-" * 30)
    
    if sys.platform.startswith('linux'):
        print("Para Linux, si hay problemas:")
        print("1. sudo apt-get update")
        print("2. sudo apt-get install python3-tk python3-pil python3-pil.imagetk")
        print("3. pip install -r requirements.txt")
        print("4. Instalar visor PDF: sudo apt-get install evince")
    elif sys.platform == "win32":
        print("Para Windows:")
        print("1. pip install -r requirements.txt")
        print("2. Asegúrese de tener un visor PDF instalado")
    else:
        print("Para macOS:")  
        print("1. pip install -r requirements.txt")
        print("2. Preview viene preinstalado como visor PDF")
    
    print()
    print("✨ Diagnóstico completado!")
    print("Si persisten los errores, comparta esta salida con soporte técnico.")

if __name__ == "__main__":
    main()