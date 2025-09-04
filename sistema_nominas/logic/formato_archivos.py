"""
Módulo para generar nombres de archivos personalizados para nóminas.
"""
import re
from datetime import datetime


def generar_nombre_archivo(plantilla, nombre, apellido="", config=None):
    """
    Genera nombre de archivo basado en plantilla personalizable.
    
    Args:
        plantilla (str): Plantilla con variables como '{nombre}_{apellido}_Nomina_{mes}_{año}.pdf'
        nombre (str): Nombre del empleado (viene de columna CSV)
        apellido (str): Apellido del empleado (viene de columna CSV)
        config: Configuración adicional (opcional)
        
    Returns:
        str: Nombre de archivo formateado
        
    Variables disponibles:
        {NOMBRE} - Nombre en mayúsculas
        {APELLIDO} - Apellido en mayúsculas  
        {nombre} - Nombre normal
        {apellido} - Apellido normal
        {mes} - Mes actual en minúsculas
        {año} - Año actual
        {MES} - Mes actual en mayúsculas
    """
    
    # Usar directamente los valores que vienen del CSV
    primer_nombre = nombre.strip() if nombre else ""
    apellido_limpio = apellido.strip() if apellido else ""
    
    # Obtener fecha actual
    ahora = datetime.now()
    meses = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    mes_actual = meses[ahora.month - 1]
    mes_actual_mayus = mes_actual.upper()
    año_actual = ahora.year
    
    # Diccionario de reemplazos
    variables = {
        'NOMBRE': primer_nombre.upper(),
        'APELLIDO': apellido_limpio.upper(),
        'nombre': primer_nombre,
        'apellido': apellido_limpio, 
        'mes': mes_actual,
        'año': str(año_actual),
        'MES': mes_actual_mayus
    }
    
    # Reemplazar variables en la plantilla
    nombre_archivo = plantilla
    for variable, valor in variables.items():
        nombre_archivo = nombre_archivo.replace(f'{{{variable}}}', valor)
    
    # Limpiar caracteres inválidos para nombres de archivo
    nombre_archivo = limpiar_nombre_archivo(nombre_archivo)
    
    return nombre_archivo


def limpiar_nombre_archivo(nombre):
    """
    Limpia caracteres inválidos para nombres de archivo.
    
    Args:
        nombre (str): Nombre de archivo a limpiar
        
    Returns:
        str: Nombre limpio y válido
    """
    # Characters not allowed in filenames across operating systems
    caracteres_invalidos = r'[<>:"/\\|?*]'
    
    # Replace invalid characters with underscore
    nombre_limpio = re.sub(caracteres_invalidos, '_', nombre)
    
    # Remove extra spaces and replace multiple spaces with single space
    nombre_limpio = re.sub(r'\s+', ' ', nombre_limpio.strip())
    
    # Replace spaces with underscore (optional, for better compatibility)
    # nombre_limpio = nombre_limpio.replace(' ', '_')
    
    return nombre_limpio


def obtener_formatos_predefinidos():
    """
    Devuelve formatos predefinidos para diferentes casos de uso.
    
    Returns:
        dict: Diccionario con formatos predefinidos
    """
    return {
        'empresarial': '{NOMBRE}_{APELLIDO}_Nomina_{mes}_{año}.pdf',
        'simple': 'nomina_{nombre}.pdf',
        'con_fecha': '{año}_{mes}_{nombre}_{apellido}.pdf',
        'clasico': 'nomina_{nombre}_{apellido}.pdf',
        'formal': '{APELLIDO}_{NOMBRE}_Nomina_{MES}_{año}.pdf'
    }


def validar_plantilla(plantilla):
    """
    Valida que una plantilla sea correcta.
    
    Args:
        plantilla (str): Plantilla a validar
        
    Returns:
        tuple: (es_valida, mensaje_error)
    """
    if not plantilla or not isinstance(plantilla, str):
        return False, "La plantilla no puede estar vacía"
    
    # Verify template ends with .pdf extension
    if not plantilla.lower().endswith('.pdf'):
        return False, "La plantilla debe terminar en '.pdf'"
    
    # Verify only valid template variables are used
    variables_validas = {'NOMBRE', 'APELLIDO', 'nombre', 'apellido', 'mes', 'año', 'MES'}
    variables_encontradas = set(re.findall(r'\{(\w+)\}', plantilla))
    
    variables_invalidas = variables_encontradas - variables_validas
    if variables_invalidas:
        return False, f"Variables no válidas: {', '.join(variables_invalidas)}"
    
    # Verify template doesn't contain problematic characters
    caracteres_problematicos = '<>:"/\\|?*'
    for char in caracteres_problematicos:
        if char in plantilla:
            return False, f"Carácter no permitido: '{char}'"
    
    return True, "Plantilla válida"


def generar_ejemplo_archivo(plantilla):
    """
    Genera un ejemplo de nombre de archivo con datos ficticios.
    
    Args:
        plantilla (str): Plantilla a probar
        
    Returns:
        str: Ejemplo de nombre generado
    """
    return generar_nombre_archivo(plantilla, "María", "García")