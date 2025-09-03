import configparser
import os
import shutil
from tkinter import messagebox

SETTINGS_FILE = 'settings.ini'
TEMPLATE_FILE = 'settings_template.ini'

try:
    from logic.security import (
        encrypt_sensitive_config, 
        decrypt_sensitive_config, 
        is_first_run, 
        create_default_config
    )
    ENCRYPTION_AVAILABLE = True
except ImportError:
    # Si falla la importación (falta cryptography), usar sin cifrado
    ENCRYPTION_AVAILABLE = False
    messagebox.showwarning(
        "Cifrado no disponible",
        "La librería de cifrado no está instalada.\n"
        "Las contraseñas se guardarán en texto plano.\n"
        "Para mayor seguridad, instale: pip install cryptography"
    )


def load_settings():
    """Carga la configuración desde settings.ini con descifrado automático."""
    config = configparser.ConfigParser()
    
    # Primera ejecución - crear configuración por defecto
    if not os.path.exists(SETTINGS_FILE):
        if ENCRYPTION_AVAILABLE:
            config = create_default_config()
        else:
            config['Email'] = {'email_origen': '', 'password': ''}
            config['SMTP'] = {'servidor': 'smtp.gmail.com', 'puerto': '587'}
            config['Carpetas'] = {'salida': 'nominas_individuales'}
            config['PDF'] = {'password_autor': ''}
        save_settings(config)
        return config
    
    # Cargar configuración existente
    config.read(SETTINGS_FILE, encoding='utf-8')
    
    # Validar secciones mínimas
    if 'Email' not in config:
        config['Email'] = {'email_origen': '', 'password': ''}
    if 'SMTP' not in config:
        config['SMTP'] = {'servidor': 'smtp.gmail.com', 'puerto': '587'}
    if 'Carpetas' not in config:
        config['Carpetas'] = {'salida': 'nominas_individuales'}
    if 'PDF' not in config:
        config['PDF'] = {'password_autor': ''}
    
    # Descifrar si está disponible
    if ENCRYPTION_AVAILABLE:
        config = decrypt_sensitive_config(config)
    
    return config


def save_settings(config):
    """Guarda la configuración en settings.ini con cifrado automático."""
    # Hacer backup de la configuración actual
    if os.path.exists(SETTINGS_FILE):
        try:
            shutil.copy(SETTINGS_FILE, SETTINGS_FILE + '.backup')
        except:
            pass  # Fallar silenciosamente si no se puede hacer backup
    
    try:
        # Cifrar campos sensibles si está disponible
        if ENCRYPTION_AVAILABLE:
            config_to_save = encrypt_sensitive_config(config)
        else:
            config_to_save = config
        
        # Guardar configuración
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as configfile:
            config_to_save.write(configfile)
            
    except Exception as e:
        # Si falla, restaurar backup
        if os.path.exists(SETTINGS_FILE + '.backup'):
            shutil.copy(SETTINGS_FILE + '.backup', SETTINGS_FILE)
        raise Exception(f"Error al guardar configuración: {e}")
    
    # Limpiar backup si todo fue bien
    if os.path.exists(SETTINGS_FILE + '.backup'):
        try:
            os.remove(SETTINGS_FILE + '.backup')
        except:
            pass


def reset_settings():
    """Resetea la configuración a valores por defecto."""
    if os.path.exists(SETTINGS_FILE):
        try:
            os.remove(SETTINGS_FILE)
        except:
            pass
    
    # Limpiar archivo de clave si existe
    if ENCRYPTION_AVAILABLE and os.path.exists('.secret_key'):
        try:
            os.remove('.secret_key')
        except:
            pass
