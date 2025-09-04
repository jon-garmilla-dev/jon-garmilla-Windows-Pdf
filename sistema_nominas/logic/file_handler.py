import pandas as pd
import fitz  # PyMuPDF
import re


def leer_cabeceras_empleados(filepath):
    """Read column headers from a CSV or Excel file.
    
    Extracts only the column names without loading the full dataset.
    Useful for mapping columns before processing the complete file.
    
    Args:
        filepath (str): Path to the CSV or Excel file
        
    Returns:
        list: Column names from the file, empty list if error occurs
    """
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
    """Read employee data file, automatically detecting CSV or Excel format.
    
    Args:
        filepath (str): Path to the employee data file
        
    Returns:
        pandas.DataFrame: Employee data
        
    Raises:
        ValueError: If file format is not supported
    """
    if filepath.endswith('.csv'):
        return pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        return pd.read_excel(filepath)
    else:
        raise ValueError("Formato de archivo no soportado.")


def analizar_archivos(pdf_path, empleados_path, columnas_map):
    """Analyze PDF and employee files to create processing tasks.
    
    Extracts NIFs from each PDF page and matches them with employee data.
    Creates task objects that contain all information needed for payroll processing.
    
    Args:
        pdf_path (str): Path to the master PDF file containing all payrolls
        empleados_path (str): Path to the employee data file (CSV/Excel)
        columnas_map (dict): Mapping of required fields to actual column names
        
    Returns:
        dict: Contains 'tareas' list with task objects, or 'error' message if failed
    """
    try:
        df = leer_archivo_empleados(empleados_path)
        for col_key, col_name in columnas_map.items():
            if col_name not in df.columns:
                raise ValueError(
                    f"Column '{col_name}' mapped to '{col_key}' "
                    f"not found in file."
                )
    except Exception as e:
        return {"error": f"Error reading employee file:\n{e}"}

    doc_maestro = fitz.open(pdf_path)
    tareas = []
    
    for num_pagina in range(len(doc_maestro)):
        texto_pagina = doc_maestro.load_page(num_pagina).get_text()
        nif_match = re.search(r'\b(\d{8}[A-Z])\b', texto_pagina)
        
        tarea = {
            "pagina": num_pagina + 1, "nif": "N/A", "nombre": "N/A",
            "apellidos": "N/A", "email": "N/A", "status": "[ADVERTENCIA] Sin NIF en PDF"}
        if nif_match:
            nif = nif_match.group(1)
            tarea["nif"] = nif
            info = df[df[columnas_map["nif"]] == nif]
            if not info.empty:
                nombre_solo = info.iloc[0][columnas_map["nombre"]]
                if "apellidos" in columnas_map and columnas_map["apellidos"]:
                    apellidos_campo = info.iloc[0][columnas_map["apellidos"]]
                else:
                    apellidos_campo = ""
                
                posicion_original = None
                if "POS." in df.columns:
                    posicion_original = info.iloc[0]["POS."]
                
                tarea.update({
                    "nombre": nombre_solo,  # First name only, without last name
                    "apellidos": apellidos_campo,  # Last name separate field
                    "email": info.iloc[0][columnas_map["email"]],
                    "posicion_original": posicion_original,  # Maintain original order
                    "status": "[OK]"
                })
            else:
                tarea["status"] = "[ERROR] NIF no encontrado en la lista"
        tareas.append(tarea)
        
    doc_maestro.close()
    return {"tareas": tareas}
