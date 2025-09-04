"""
Módulo para el manejo de plantillas de email personalizables.
"""
from datetime import datetime
from utils.logger import log_debug


def generar_asunto_personalizado(config, nombre, apellidos):
    """Genera el asunto del email usando la plantilla configurada."""
    # Obtener plantilla de asunto desde configuración
    asunto_template = config.get('Email', 'asunto', fallback='Tu nómina de {mes} {año}')
    
    # Variables available for template replacement
    variables = _obtener_variables_email(nombre, apellidos)
    
    # Replace template variables with actual values
    asunto_final = asunto_template
    for variable, valor in variables.items():
        asunto_final = asunto_final.replace(f'{{{variable}}}', valor)
    
    log_debug(f"Asunto generado: {asunto_final}")
    return asunto_final


def generar_cuerpo_personalizado(config, nombre, apellidos):
    """Genera el cuerpo del email usando la plantilla configurada."""
    # Obtener plantilla de cuerpo desde configuración
    cuerpo_template = config.get('Email', 'cuerpo_mensaje', fallback='''Hola {nombre},

Adjuntamos tu nómina correspondiente al mes de {mes} de {año}.
La contraseña para abrir el archivo es tu NIF.

Saludos cordiales.''')
    
    # Variables available for template replacement
    variables = _obtener_variables_email(nombre, apellidos)
    
    # Replace template variables with actual values
    cuerpo_final = cuerpo_template
    for variable, valor in variables.items():
        cuerpo_final = cuerpo_final.replace(f'{{{variable}}}', valor)
    
    log_debug(f"Cuerpo generado para {nombre}")
    return cuerpo_final


def _obtener_variables_email(nombre, apellidos):
    """Obtiene el diccionario de variables disponibles para las plantillas."""
    fecha_actual = datetime.now()
    mes_nombre = {
        1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
        7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
    }[fecha_actual.month]
    
    return {
        'nombre': nombre,
        'apellidos': apellidos,
        'mes': mes_nombre,
        'año': str(fecha_actual.year)
    }


