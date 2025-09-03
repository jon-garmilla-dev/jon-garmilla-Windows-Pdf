import base64
import os
from cryptography.fernet import Fernet
import configparser

SETTINGS_FILE = 'settings.ini'
KEY_FILE = '.secret_key'


def generate_key():
    """Genera una clave de cifrado única para el usuario."""
    return Fernet.generate_key()


def get_or_create_key():
    """Obtiene la clave existente o crea una nueva."""
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        key = generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
        # Hacer el archivo de clave oculto en Windows
        if os.name == 'nt':
            import subprocess
            try:
                subprocess.check_call(['attrib', '+H', KEY_FILE])
            except:
                pass  # Fallar silenciosamente si no se puede ocultar
    return key


def encrypt_string(text, key):
    """Cifra una cadena de texto."""
    if not text:
        return text
    f = Fernet(key)
    return base64.urlsafe_b64encode(f.encrypt(text.encode())).decode()


def decrypt_string(encrypted_text, key):
    """Descifra una cadena de texto."""
    if not encrypted_text or not encrypted_text.startswith('enc_'):
        return encrypted_text  # No está cifrado
    try:
        f = Fernet(key)
        # Remover el prefijo 'enc_'
        encrypted_data = encrypted_text[4:]
        decrypted_bytes = f.decrypt(base64.urlsafe_b64decode(encrypted_data.encode()))
        return decrypted_bytes.decode()
    except:
        return encrypted_text  # Si falla la desencriptación, devolver original


def encrypt_sensitive_config(config):
    """Cifra los campos sensibles de la configuración."""
    key = get_or_create_key()
    
    sensitive_fields = {
        'Email': ['password'],
        'PDF': ['password_autor']
    }
    
    for section_name, fields in sensitive_fields.items():
        if section_name in config:
            for field in fields:
                if field in config[section_name]:
                    original_value = config[section_name][field]
                    if original_value and not original_value.startswith('enc_'):
                        encrypted_value = 'enc_' + encrypt_string(original_value, key)
                        config.set(section_name, field, encrypted_value)
    
    return config


def decrypt_sensitive_config(config):
    """Descifra los campos sensibles de la configuración."""
    key = get_or_create_key()
    
    # Crear una nueva configuración con valores descifrados
    decrypted_config = configparser.ConfigParser()
    
    for section_name in config.sections():
        decrypted_config.add_section(section_name)
        for option_name in config.options(section_name):
            encrypted_value = config.get(section_name, option_name)
            decrypted_value = decrypt_string(encrypted_value, key)
            decrypted_config.set(section_name, option_name, decrypted_value)
    
    return decrypted_config


def is_first_run():
    """Verifica si es la primera vez que se ejecuta la aplicación."""
    return not os.path.exists(SETTINGS_FILE) or not os.path.exists(KEY_FILE)


def create_default_config():
    """Crea una configuración por defecto para el primer uso."""
    config = configparser.ConfigParser()
    
    config['Email'] = {
        'email_origen': '',
        'password': ''
    }
    
    config['SMTP'] = {
        'servidor': 'smtp.gmail.com',
        'puerto': '587'
    }
    
    config['Carpetas'] = {
        'salida': 'nominas_individuales'
    }
    
    config['PDF'] = {
        'password_autor': ''
    }
    
    return config