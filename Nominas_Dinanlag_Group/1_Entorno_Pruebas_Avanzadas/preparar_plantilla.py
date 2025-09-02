import fitz
import os
import pikepdf

# --- CONFIGURACIÓN ---
# Construir rutas basadas en la ubicación del script para mayor robustez
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROYECTO_DIR = os.path.dirname(SCRIPT_DIR)

PDF_ORIGINAL = os.path.join(
    PROYECTO_DIR, "input_pdfs", "JOSUNE ANGOITIA_Nómina Agosto 2025.pdf"
)
CONTRASENA_PROPIETARIO = "DpAdmon2025"
NIF_A_REEMPLAZAR = "30632707L"
TEXTO_PLACEHOLDER = "XXXXXXXXL"
CARPETA_PLANTILLAS = os.path.join(SCRIPT_DIR, "plantillas")
NOMBRE_PLANTILLA_FINAL = "plantilla_nomina.pdf"

def preparar_plantilla():
    """
    Abre un PDF protegido, lo guarda sin protección, busca un NIF específico,
    lo reemplaza con un placeholder y guarda la plantilla final.
    """
    print("Iniciando la preparación de la plantilla...")

    # Verificar que el PDF original existe
    if not os.path.exists(PDF_ORIGINAL):
        print(
            f"❌ Error: No se encuentra el archivo PDF original en "
            f"'{PDF_ORIGINAL}'"
        )
        return

    # Usar rutas absolutas para evitar ambigüedades
    ruta_temporal = os.path.join(SCRIPT_DIR, "temp_desencriptado.pdf")
    ruta_plantilla_final = os.path.join(CARPETA_PLANTILLAS, NOMBRE_PLANTILLA_FINAL)

    # Paso 1: Usar pikepdf para quitar la protección por contraseña
    try:
        with pikepdf.open(
            PDF_ORIGINAL,
            password=CONTRASENA_PROPIETARIO,
            allow_overwriting_input=True
        ) as pdf:
            pdf.save(ruta_temporal)
        print("✅ PDF desencriptado y guardado temporalmente.")
    except Exception as e:
        print(f"❌ Error al desencriptar el PDF con pikepdf: {e}")
        return

    # Paso 2: Usar PyMuPDF para buscar y reemplazar el NIF
    try:
        doc = fitz.open(ruta_temporal)
        pagina = doc.load_page(0)
        
        rectangulos = pagina.search_for(NIF_A_REEMPLAZAR)
        
        if not rectangulos:
            print(
                f"⚠️  Aviso: No se encontró el NIF '{NIF_A_REEMPLAZAR}' en el "
                "documento."
            )
        else:
            # Reemplazar todas las ocurrencias encontradas
            for rect in rectangulos:
                # Cubrir con un cuadro blanco
                pagina.add_redact_annot(rect, fill=(1, 1, 1))
            pagina.apply_redactions()
            
            # Insertar el placeholder en la posición del primer NIF encontrado
            pagina.insert_text(
                rectangulos[0].bottom_left,
                TEXTO_PLACEHOLDER,
                fontsize=8,
                fontname="helv",
                color=(0, 0, 0)
            )
            print(
                f"✅ NIF '{NIF_A_REEMPLAZAR}' reemplazado por "
                f"'{TEXTO_PLACEHOLDER}'."
            )

        doc.save(ruta_plantilla_final)
        doc.close()
        print(f"✅ Plantilla final guardada en '{ruta_plantilla_final}'.")

    except Exception as e:
        print(f"❌ Error al reemplazar el NIF con PyMuPDF: {e}")
    
    # Paso 3: Limpiar el archivo temporal
    finally:
        if os.path.exists(ruta_temporal):
            os.remove(ruta_temporal)
            print("  -> Archivo temporal eliminado.")


if __name__ == "__main__":
    preparar_plantilla()
