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
        create_default_config
    )
    ENCRYPTION_AVAILABLE = True
except ImportError:
    # Handle missing cryptography library gracefully
    # Application will function but passwords will be stored in plain text
    ENCRYPTION_AVAILABLE = False
    messagebox.showwarning(
        "Encryption Unavailable",
        "The cryptography library is not installed.\n"
        "Passwords will be stored in plain text.\n"
        "For enhanced security, install: pip install cryptography"
    )


def load_settings():
    """Load application configuration from settings.ini with automatic decryption.
    
    Handles first-time setup by creating default configuration if no settings file exists.
    Validates and ensures all required configuration sections are present.
    Automatically decrypts sensitive fields when encryption is available.
    
    Returns:
        ConfigParser: Configuration object with decrypted sensitive data
    """
    config = configparser.ConfigParser()
    
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
    
    config.read(SETTINGS_FILE, encoding='utf-8')
    
    if 'Email' not in config:
        config['Email'] = {'email_origen': '', 'password': ''}
    if 'SMTP' not in config:
        config['SMTP'] = {'servidor': 'smtp.gmail.com', 'puerto': '587'}
    if 'Carpetas' not in config:
        config['Carpetas'] = {'salida': 'nominas_individuales'}
    if 'PDF' not in config:
        config['PDF'] = {'password_autor': ''}
    if 'Formato' not in config:
        config['Formato'] = {
            'archivo_nomina': '{nombre}_{apellidos}_Nomina_{mes}_{año}.pdf'
        }
    if 'UltimosArchivos' not in config:
        config['UltimosArchivos'] = {
            'pdf_maestro': '',
            'excel_empleados': ''
        }
    
    if ENCRYPTION_AVAILABLE:
        config = decrypt_sensitive_config(config)
    
    return config


def save_settings(config):
    """Save configuration to settings.ini with automatic encryption.
    
    Creates backup of current settings before saving to prevent data loss.
    Encrypts sensitive fields when encryption is available.
    Restores backup if save operation fails.
    
    Args:
        config (ConfigParser): Configuration object to save
        
    Raises:
        Exception: If save operation fails after backup restoration
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            shutil.copy(SETTINGS_FILE, SETTINGS_FILE + '.backup')
        except OSError:
            pass  # Fail silently if backup cannot be created
    
    try:
            if ENCRYPTION_AVAILABLE:
            config_to_save = encrypt_sensitive_config(config)
        else:
            config_to_save = config
        
            with open(SETTINGS_FILE, 'w', encoding='utf-8') as configfile:
            config_to_save.write(configfile)
            
    except Exception as e:
            if os.path.exists(SETTINGS_FILE + '.backup'):
            shutil.copy(SETTINGS_FILE + '.backup', SETTINGS_FILE)
        raise Exception(f"Error al guardar configuración: {e}")
    
    if os.path.exists(SETTINGS_FILE + '.backup'):
        try:
            os.remove(SETTINGS_FILE + '.backup')
        except OSError:
            pass


def reset_settings():
    """Reset configuration to default values.
    
    Removes existing settings file and encryption key file.
    Next application start will create fresh default configuration.
    """
    if os.path.exists(SETTINGS_FILE):
        try:
            os.remove(SETTINGS_FILE)
        except OSError:
            pass
    
    if ENCRYPTION_AVAILABLE and os.path.exists('.secret_key'):
        try:
            os.remove('.secret_key')
        except OSError:
            pass
