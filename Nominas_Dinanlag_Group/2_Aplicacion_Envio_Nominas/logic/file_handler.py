import pandas as pd
import fitz  # PyMuPDF
import re


def leer_cabeceras_empleados(filepath):
    """Lee solo las cabeceras de un archivo CSV o Excel."""
    try:
        if filepath.endswith('.csv'):
            return pd.read_csv(filepath, nrows=0).columns.tolist()
        elif filepath.endswith(('.xlsx', '.xls')):
            return pd.read_excel(filepath, nrows=0).columns.tolist()
        else:
            return []
    except Exception:
        return []


def leer_archivo_empleados(filepath):
    """Lee un archivo de empleados, detectando si es CSV o Excel."""
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Formato de archivo no soportado.")


def analizar_archivos(pdf_path, empleados_path, columnas_map):
    """Analiza los archivos con el mapeo de columnas y devuelve una lista de tareas."""
    try:
        df = leer_archivo_empleados(empleados_path)
        # Validar que las columnas mapeadas existen en el DataFrame
        for col_key, col_name in columnas_map.items():
            if col_name not in df.columns:
                raise ValueError(
                    f"La columna '{col_name}' asignada a '{col_key}' no se "
                    f"encuentra en el archivo."
                )
    except Exception as e:
        return {"error": f"Error al leer el archivo de empleados:\n{e}"}

    doc_maestro = fitz.open(pdf_path)
    tareas = []
    
    for num_pagina in range(len(doc_maestro)):
        texto_pagina = doc_maestro.load_page(num_pagina).get_text()
        nif_match = re.search(r'\b(\d{8}[A-Z])\b', texto_pagina)
        
        tarea = {
            "pagina": num_pagina + 1, "nif": "N/A", "nombre": "N/A",
            "apellidos": "N/A", "email": "N/A", "status": "⚠️ Sin NIF en PDF"}
        if nif_match:
            nif = nif_match.group(1)
            tarea["nif"] = nif
            # Usar el mapeo de columnas para la búsqueda
            info = df[df[columnas_map["nif"]] == nif]
            if not info.empty:
                # Mantener nombre y apellidos separados (NO juntar)
                nombre_solo = info.iloc[0][columnas_map["nombre"]]
                if "apellidos" in columnas_map and columnas_map["apellidos"]:
                    apellidos_campo = info.iloc[0][columnas_map["apellidos"]]
                else:
                    apellidos_campo = ""
                
                tarea.update({
                    "nombre": nombre_solo,  # Solo el nombre, sin apellidos
                    "apellidos": apellidos_campo,  # Apellidos separados
                    "email": info.iloc[0][columnas_map["email"]],
                    "status": "✅ OK"
                })
            else:
                tarea["status"] = "❌ NIF no encontrado en la lista"
        tareas.append(tarea)
        
    doc_maestro.close()
    return {"tareas": tareas}
