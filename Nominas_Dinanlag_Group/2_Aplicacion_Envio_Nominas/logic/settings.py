import configparser
import os

SETTINGS_FILE = 'settings.ini'


def load_settings():
    """Carga la configuración desde settings.ini."""
    config = configparser.ConfigParser()
    if os.path.exists(SETTINGS_FILE):
        config.read(SETTINGS_FILE)
    if 'Email' not in config:
        config['Email'] = {'email_origen': '', 'password': ''}
    return config


def save_settings(config):
    """Guarda la configuración en settings.ini."""
    with open(SETTINGS_FILE, 'w') as configfile:
        config.write(configfile)
