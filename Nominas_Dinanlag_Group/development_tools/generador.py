import fitz
import random
import os
import csv

# --- CONFIGURACIÓN ---
NUM_NOMINAS_A_GENERAR = 50
NIF_PLACEHOLDER = "XXXXXXXXL"
CARPETA_PLANTILLAS = "plantillas"
PLANTILLA_BASE = os.path.join(CARPETA_PLANTILLAS, "plantilla_nomina.pdf")
CARPETA_SALIDA_PDF = "nominas_generadas"
OUTPUT_PDF_MAESTRO = os.path.join(CARPETA_SALIDA_PDF, "nominas_Dinanlag_group.pdf")
OUTPUT_CSV_EMPLEADOS = os.path.join(CARPETA_SALIDA_PDF, "empleados_falsos.csv")

# --- FUNCIONES AUXILIARES ---

def generar_nif():
    """Genera un NIF español falso pero con letra válida."""
    letras = "TRWAGMYFPDXBNJZSQVHLCKE"
    numeros = random.randint(10000000, 99999999)
    letra = letras[numeros % 23]
    return f"{numeros}{letra}"

def generar_datos_empleados(lista_nifs):
    """Genera el archivo CSV con los datos de los empleados falsos."""
    print(f"\nGenerando archivo CSV: '{OUTPUT_CSV_EMPLEADOS}'...")
    with open(OUTPUT_CSV_EMPLEADOS, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['NIF', 'NOMBRE', 'EMAIL'])
        for i, nif in enumerate(lista_nifs):
            nombre = f"Empleado Falso {i+1}"
            email = f"empleado.falso.{i+1}@empresa-ejemplo.com"
            writer.writerow([nif, nombre, email])
    print("✅ Archivo CSV generado con éxito.")

# --- SCRIPT PRINCIPAL ---

def crear_pdf_maestro():
    print("Iniciando la generación del PDF maestro de nóminas falsas...")

    if not os.path.exists(PLANTILLA_BASE):
        print(f"❌ Error: No se encuentra el archivo de plantilla '{PLANTILLA_BASE}'.")
        return

    doc_maestro = fitz.open() 
    nifs_generados = []

    for i in range(NUM_NOMINAS_A_GENERAR):
        nuevo_nif = generar_nif()
        while nuevo_nif in nifs_generados:
            nuevo_nif = generar_nif()
        nifs_generados.append(nuevo_nif)

        doc_plantilla = fitz.open(PLANTILLA_BASE)
        pagina = doc_plantilla.load_page(0)

        rectangulos = pagina.search_for(NIF_PLACEHOLDER)
        if not rectangulos:
            print(f"⚠️  Aviso: No se encontró '{NIF_PLACEHOLDER}' en la plantilla.")
            continue
        
        rect_nif = rectangulos[0]
        pagina.add_redact_annot(rect_nif, fill=(1, 1, 1))
        pagina.apply_redactions()
        pagina.insert_text(rect_nif.bottom_left, nuevo_nif, fontsize=8, fontname="helv", color=(0, 0, 0))
        
        doc_maestro.insert_pdf(doc_plantilla)
        doc_plantilla.close()

        print(f"({i+1}/{NUM_NOMINAS_A_GENERAR}) Nómina generada con NIF {nuevo_nif} y añadida al PDF maestro.")

    num_paginas_final = len(doc_maestro)
    doc_maestro.save(OUTPUT_PDF_MAESTRO)
    doc_maestro.close()

    print(
        f"\n✅ PDF maestro '{OUTPUT_PDF_MAESTRO}' con {num_paginas_final} "
        "páginas generado con éxito."
    )
    
    generar_datos_empleados(nifs_generados)


if __name__ == "__main__":
    crear_pdf_maestro()
