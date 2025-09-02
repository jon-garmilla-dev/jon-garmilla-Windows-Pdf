import fitz
import os
import pandas as pd
import re

# --- CONFIGURACIÓN ---
CARPETA_ENTRADA = "nominas_generadas"
PDF_MAESTRO = os.path.join(CARPETA_ENTRADA, "nominas_Dinanlag_group.pdf")
CSV_EMPLEADOS = os.path.join(CARPETA_ENTRADA, "empleados_falsos.csv")
CARPETA_SALIDA = "nominas_divididas"


# --- SCRIPT PRINCIPAL ---

def dividir_pdf_maestro():
    print("Iniciando el proceso de división del PDF maestro...")

    # Verificar que los archivos de entrada existen
    if not os.path.exists(PDF_MAESTRO):
        print(f"❌ Error: No se encuentra el PDF maestro en '{PDF_MAESTRO}'.")
        return
    if not os.path.exists(CSV_EMPLEADOS):
        print(f"❌ Error: No se encuentra el archivo CSV en '{CSV_EMPLEADOS}'.")
        return

    # Cargar los datos de los empleados desde el CSV
    try:
        df_empleados = pd.read_csv(CSV_EMPLEADOS)
    except Exception as e:
        print(f"❌ Error al leer el archivo CSV: {e}")
        return

    doc_maestro = fitz.open(PDF_MAESTRO)
    print(f"Procesando {len(doc_maestro)} páginas del PDF maestro...")

    for num_pagina in range(len(doc_maestro)):
        pagina = doc_maestro.load_page(num_pagina)
        texto_pagina = pagina.get_text()
        
        resultado_nif = re.search(r'\b(\d{8}[A-Z])\b', texto_pagina)
        
        if resultado_nif:
            nif_encontrado = resultado_nif.group(1)
            
            # Buscar el NIF en nuestro DataFrame de empleados
            info_empleado = df_empleados[df_empleados['NIF'] == nif_encontrado]
            
            if not info_empleado.empty:
                nombre_empleado = info_empleado.iloc[0]['NOMBRE']
                
                # Crear un nombre de archivo descriptivo
                nombre_archivo = (
                    f"{nombre_empleado.replace(' ', '_')}_nomina.pdf"
                )
                ruta_salida = os.path.join(CARPETA_SALIDA, nombre_archivo)
                
                # Crear un nuevo PDF con la página individual
                doc_individual = fitz.open()
                doc_individual.insert_pdf(
                    doc_maestro, from_page=num_pagina, to_page=num_pagina
                )
                doc_individual.save(ruta_salida)
                doc_individual.close()
                
                print(
                    f"  -> Página {num_pagina + 1}: NIF {nif_encontrado} -> "
                    f"Guardada como '{ruta_salida}'"
                )
            else:
                print(
                    f"  -> Página {num_pagina + 1}: NIF {nif_encontrado} no "
                    "encontrado en el CSV."
                )
        else:
            print(f"  -> Página {num_pagina + 1}: No se encontró NIF.")
            
    doc_maestro.close()
    print("\n✅ Proceso de división finalizado.")


if __name__ == "__main__":
    dividir_pdf_maestro()
