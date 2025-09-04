import base64
import os
from cryptography.fernet import Fernet
import configparser

SETTINGS_FILE = 'settings.ini'
KEY_FILE = '.secret_key'


def generate_key():
    """Generate a unique encryption key for the user.
    
    Returns:
        bytes: Cryptographically secure random key for Fernet encryption
    """
    return Fernet.generate_key()


def get_or_create_key():
    """Get existing encryption key or create a new one.
    
    Loads key from hidden file if it exists, otherwise generates new key.
    On Windows, attempts to set hidden attribute on key file for security.
    
    Returns:
        bytes: Encryption key for use with Fernet
    """
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            key = key_file.read()
    else:
        key = generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)
        # Set hidden attribute on key file in Windows for security
        if os.name == 'nt':
            import subprocess
            try:
                subprocess.check_call(['attrib', '+H', KEY_FILE])
            except:
                pass
    return key


def encrypt_string(text, key):
    """Encrypt a text string using Fernet symmetric encryption.
    
    Args:
        text (str): Plain text to encrypt
        key (bytes): Fernet encryption key
        
    Returns:
        str: Base64-encoded encrypted text, or original text if empty
    """
    if not text:
        return text
    f = Fernet(key)
    return base64.urlsafe_b64encode(f.encrypt(text.encode())).decode()


def decrypt_string(encrypted_text, key):
    """Decrypt a text string using Fernet symmetric encryption.
    
    Handles both encrypted and plain text values safely.
    Only attempts decryption if text starts with 'enc_' prefix.
    
    Args:
        encrypted_text (str): Text to decrypt (may be plain or encrypted)
        key (bytes): Fernet encryption key
        
    Returns:
        str: Decrypted plain text, or original text if not encrypted/decryption fails
    """
    if not encrypted_text or not encrypted_text.startswith('enc_'):
        return encrypted_text  # Text is not encrypted
    try:
        f = Fernet(key)
        # Remove the 'enc_' prefix before decryption
        encrypted_data = encrypted_text[4:]
        decrypted_bytes = f.decrypt(base64.urlsafe_b64decode(encrypted_data.encode()))
        return decrypted_bytes.decode()
    except:
        return encrypted_text  # Return original if decryption fails


def encrypt_sensitive_config(config):
    """Encrypt sensitive fields in configuration object.
    
    Encrypts password fields and other sensitive configuration values.
    Only encrypts values that are not already encrypted (no 'enc_' prefix).
    
    Args:
        config (ConfigParser): Configuration object to encrypt
        
    Returns:
        ConfigParser: Configuration object with encrypted sensitive fields
    """
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
    """Decrypt sensitive fields in configuration object.
    
    Creates a new configuration object with decrypted sensitive values.
    Handles both encrypted and plain text values gracefully.
    
    Args:
        config (ConfigParser): Configuration object with encrypted fields
        
    Returns:
        ConfigParser: New configuration object with decrypted sensitive fields
    """
    key = get_or_create_key()
    
    # Create new configuration object with decrypted values
    decrypted_config = configparser.ConfigParser()
    
    for section_name in config.sections():
        decrypted_config.add_section(section_name)
        for option_name in config.options(section_name):
            encrypted_value = config.get(section_name, option_name)
            decrypted_value = decrypt_string(encrypted_value, key)
            decrypted_config.set(section_name, option_name, decrypted_value)
    
    return decrypted_config


def is_first_run():
    """Check if this is the first application run.
    
    Returns:
        bool: True if settings file or encryption key file is missing
    """
    return not os.path.exists(SETTINGS_FILE) or not os.path.exists(KEY_FILE)


def create_default_config():
    """Create default configuration for first-time use.
    
    Sets up initial configuration sections with empty values that user can fill.
    Includes email, SMTP, folders, and PDF password settings.
    
    Returns:
        ConfigParser: Default configuration object
    """
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