"""
Sistema de notificaciones sonoras para la aplicación de nóminas.
Genera sonidos profesionales usando la librería estándar de Python.
"""
import platform
import threading
import time
from utils.logger import log_debug, log_warning


class SoundManager:
    """Gestor de sonidos para notificaciones empresariales."""
    
    def __init__(self):
        self.enabled = True
        self._setup_sound_system()
    
    def _setup_sound_system(self):
        """Configura el sistema de sonidos según la plataforma."""
        self.system = platform.system()
        log_debug(f"Iniciando sistema de sonidos para {self.system}")
        
    def _play_system_sound(self, sound_type):
        """Reproduce sonidos usando APIs nativas del sistema."""
        if not self.enabled:
            return
            
        try:
            if self.system == 'Windows':
                self._play_windows_sound(sound_type)
            elif self.system == 'Darwin':  # macOS
                self._play_macos_sound(sound_type)
            else:  # Linux
                self._play_linux_sound(sound_type)
        except Exception as e:
            log_warning(f"No se pudo reproducir sonido {sound_type}: {e}")
    
    def _play_windows_sound(self, sound_type):
        """Reproduce sonidos nativos de Windows."""
        import winsound
        
        sound_map = {
            'success': winsound.MB_OK,
            'error': winsound.MB_ICONHAND,
            'warning': winsound.MB_ICONEXCLAMATION
        }
        
        if sound_type in sound_map:
            winsound.MessageBeep(sound_map[sound_type])
            log_debug(f"Reproducido sonido Windows: {sound_type}")
    
    def _play_macos_sound(self, sound_type):
        """Reproduce sonidos nativos de macOS."""
        import subprocess
        
        sound_map = {
            'success': 'Glass',
            'error': 'Basso',
            'warning': 'Ping'
        }
        
        if sound_type in sound_map:
            subprocess.run(['afplay', f'/System/Library/Sounds/{sound_map[sound_type]}.aiff'], 
                         capture_output=True, check=False)
            log_debug(f"Reproducido sonido macOS: {sound_type}")
    
    def _play_linux_sound(self, sound_type):
        """Reproduce sonidos en Linux usando múltiples métodos."""
        import subprocess
        
        # Intentar diferentes métodos en orden de preferencia
        methods = [
            self._try_paplay,
            self._try_aplay,
            self._try_speaker_beep,
            self._try_bell
        ]
        
        for method in methods:
            if method(sound_type):
                log_debug(f"Reproducido sonido Linux: {sound_type}")
                return
        
        log_warning(f"No se pudo reproducir sonido en Linux: {sound_type}")
    
    def _try_paplay(self, sound_type):
        """Intenta usar paplay (PulseAudio)."""
        try:
            import subprocess
            sound_files = {
                'success': '/usr/share/sounds/alsa/Front_Left.wav',
                'error': '/usr/share/sounds/alsa/Front_Right.wav', 
                'warning': '/usr/share/sounds/alsa/Side_Left.wav'
            }
            
            if sound_type in sound_files:
                result = subprocess.run(['paplay', sound_files[sound_type]], 
                                      capture_output=True, timeout=2)
                return result.returncode == 0
        except:
            pass
        return False
    
    def _try_aplay(self, sound_type):
        """Intenta usar aplay (ALSA)."""
        try:
            import subprocess
            # Generar tonos con frecuencias diferentes
            frequencies = {
                'success': '800',
                'error': '200', 
                'warning': '500'
            }
            
            if sound_type in frequencies:
                cmd = f"speaker-test -t sine -f {frequencies[sound_type]} -l 1 -s 1"
                result = subprocess.run(cmd, shell=True, capture_output=True, timeout=2)
                return result.returncode == 0
        except:
            pass
        return False
    
    def _try_speaker_beep(self, sound_type):
        """Intenta usar el altavoz del sistema."""
        try:
            import subprocess
            beep_patterns = {
                'success': [('800', '0.2'), ('1000', '0.2')],
                'error': [('200', '0.5')],
                'warning': [('500', '0.3')]
            }
            
            if sound_type in beep_patterns and subprocess.which('beep'):
                for freq, duration in beep_patterns[sound_type]:
                    subprocess.run(['beep', '-f', freq, '-l', str(int(float(duration)*1000))], 
                                 capture_output=True, timeout=2)
                return True
        except:
            pass
        return False
    
    def _try_bell(self, sound_type):
        """Último recurso: usar el bell del terminal."""
        try:
            print('\a', end='', flush=True)  # ASCII bell character
            return True
        except:
            pass
        return False
    
    def _play_async(self, sound_type):
        """Reproduce sonido en hilo separado para no bloquear la UI."""
        thread = threading.Thread(target=self._play_system_sound, 
                                 args=(sound_type,), daemon=True)
        thread.start()
    
    def play_success(self):
        """Reproduce sonido de éxito - proceso completado."""
        log_debug("Reproduciendo sonido de éxito")
        self._play_async('success')
    
    def play_error(self):
        """Reproduce sonido de error - fallo crítico."""
        log_debug("Reproduciendo sonido de error")
        self._play_async('error')
    
    def play_warning(self):
        """Reproduce sonido de advertencia - requiere atención."""
        log_debug("Reproduciendo sonido de advertencia") 
        self._play_async('warning')
    
    def set_enabled(self, enabled):
        """Habilita o deshabilita los sonidos."""
        self.enabled = enabled
        log_debug(f"Sonidos {'habilitados' if enabled else 'deshabilitados'}")
    
    def is_enabled(self):
        """Retorna si los sonidos están habilitados."""
        return self.enabled


# Instancia global del gestor de sonidos
sound_manager = SoundManager()


# Funciones helper para usar desde cualquier módulo
def play_success_sound():
    """Reproduce sonido de éxito."""
    sound_manager.play_success()


def play_error_sound():
    """Reproduce sonido de error.""" 
    sound_manager.play_error()


def play_warning_sound():
    """Reproduce sonido de advertencia."""
    sound_manager.play_warning()


def set_sounds_enabled(enabled):
    """Habilita/deshabilita los sonidos."""
    sound_manager.set_enabled(enabled)


def are_sounds_enabled():
    """Verifica si los sonidos están habilitados."""
    return sound_manager.is_enabled()