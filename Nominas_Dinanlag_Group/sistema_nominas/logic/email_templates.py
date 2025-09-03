"""
Módulo para el manejo de plantillas de email personalizables.
"""
from datetime import datetime
from utils.logger import log_debug


def generar_asunto_personalizado(config, nombre, apellidos):
    """Genera el asunto del email usando la plantilla configurada."""
    # Obtener plantilla de asunto desde configuración
    asunto_template = config.get('Email', 'asunto', fallback='Tu nómina de {mes} {año}')
    
    # Variables para reemplazo
    variables = _obtener_variables_email(nombre, apellidos)
    
    # Reemplazar variables en la plantilla
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
    
    # Variables para reemplazo
    variables = _obtener_variables_email(nombre, apellidos)
    
    # Reemplazar variables en la plantilla
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


def validar_plantilla_email(plantilla):
    """Valida que una plantilla de email tenga formato correcto."""
    if not plantilla or not isinstance(plantilla, str):
        return False, "La plantilla no puede estar vacía"
    
    # Verificar variables válidas
    variables_validas = {'nombre', 'apellidos', 'mes', 'año'}
    
    import re
    variables_encontradas = set(re.findall(r'\{(\w+)\}', plantilla))
    
    variables_invalidas = variables_encontradas - variables_validas
    if variables_invalidas:
        return False, f"Variables no válidas: {', '.join(variables_invalidas)}"
    
    return True, "Plantilla válida"


def obtener_plantillas_predefinidas():
    """Devuelve plantillas predefinidas para diferentes estilos de email."""
    return {
        'formal': {
            'asunto': 'Nómina correspondiente a {mes} {año}',
            'cuerpo': '''Estimado/a {nombre} {apellidos},

Le adjuntamos su nómina correspondiente al mes de {mes} de {año}.
La contraseña para acceder al documento es su número de identificación.

Atentamente,
Departamento de Recursos Humanos'''
        },
        'informal': {
            'asunto': 'Tu nómina de {mes} {año}',
            'cuerpo': '''Hola {nombre},

Te adjuntamos tu nómina de {mes} de {año}.
La contraseña es tu NIF.

¡Saludos!'''
        },
        'corporativo': {
            'asunto': '[NOMINA] {nombre} {apellidos} - {mes}/{año}',
            'cuerpo': '''Estimado empleado/a {nombre} {apellidos},

Por medio del presente, le hacemos entrega de su nómina correspondiente al período de {mes} de {año}.
El documento adjunto se encuentra protegido con su documento de identidad.

Quedamos a su disposición para cualquier consulta.

Cordialmente,
Área de Recursos Humanos'''
        }
    }


def aplicar_plantilla_predefinida(config, estilo):
    """Aplica una plantilla predefinida a la configuración."""
    plantillas = obtener_plantillas_predefinidas()
    
    if estilo not in plantillas:
        return False, f"Estilo '{estilo}' no disponible"
    
    plantilla = plantillas[estilo]
    
    # Aplicar a la configuración
    config.set('Email', 'asunto', plantilla['asunto'])
    config.set('Email', 'cuerpo_mensaje', plantilla['cuerpo'])
    
    return True, f"Plantilla '{estilo}' aplicada correctamente"