"""
Sound notification system for the payroll application.

Generates professional system sounds using Python standard library.
Provides cross-platform audio feedback for business operations.
"""
import platform
import threading
import time
from utils.logger import log_debug, log_warning


class SoundManager:
    """Sound manager for enterprise notifications.
    
    Provides cross-platform sound feedback for application events.
    Supports Windows, macOS, and Linux with fallback mechanisms.
    """
    
    def __init__(self):
        self.enabled = True
        self._setup_sound_system()
    
    def _setup_sound_system(self):
        """Configure sound system based on current platform.
        
        Detects operating system and prepares appropriate sound mechanisms.
        """
        self.system = platform.system()
        log_debug(f"Iniciando sistema de sonidos para {self.system}")
        
    def _play_system_sound(self, sound_type):
        """Play system sounds using native platform APIs.
        
        Args:
            sound_type (str): Type of sound to play ('success', 'error', 'warning')
        """
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
        """Play native Windows system sounds.
        
        Uses winsound module to play built-in Windows notification sounds.
        
        Args:
            sound_type (str): Sound type identifier
        """
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
        """Play native macOS system sounds.
        
        Uses afplay command to play built-in macOS system sounds.
        
        Args:
            sound_type (str): Sound type identifier
        """
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
        """Play sounds on Linux using multiple fallback methods.
        
        Tries different audio systems in order of preference:
        PulseAudio, ALSA, speaker-test, and terminal bell.
        
        Args:
            sound_type (str): Sound type identifier
        """
        import subprocess
        
        # Try different audio methods in order of preference
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
        """Attempt to use paplay (PulseAudio system).
        
        Args:
            sound_type (str): Sound type identifier
            
        Returns:
            bool: True if sound was played successfully
        """
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
        """Attempt to use aplay (ALSA system).
        
        Generates tones with different frequencies for different sound types.
        
        Args:
            sound_type (str): Sound type identifier
            
        Returns:
            bool: True if sound was played successfully
        """
        try:
            import subprocess
            # Generate tones with different frequencies for each sound type
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
        """Attempt to use system speaker for beep sounds.
        
        Uses the 'beep' command if available on the system.
        
        Args:
            sound_type (str): Sound type identifier
            
        Returns:
            bool: True if sound was played successfully
        """
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
        """Last resort: use terminal bell character.
        
        Prints ASCII bell character as fallback when other methods fail.
        
        Args:
            sound_type (str): Sound type identifier (unused in this method)
            
        Returns:
            bool: True if bell was triggered successfully
        """
        try:
            print('\a', end='', flush=True)  # ASCII bell character
            return True
        except:
            pass
        return False
    
    def _play_async(self, sound_type):
        """Play sound in separate thread to avoid blocking UI.
        
        Args:
            sound_type (str): Sound type identifier
        """
        thread = threading.Thread(target=self._play_system_sound, 
                                 args=(sound_type,), daemon=True)
        thread.start()
    
    def play_success(self):
        """Play success sound - process completed successfully."""
        log_debug("Reproduciendo sonido de éxito")
        self._play_async('success')
    
    def play_error(self):
        """Play error sound - critical failure occurred."""
        log_debug("Reproduciendo sonido de error")
        self._play_async('error')
    
    def play_warning(self):
        """Play warning sound - attention required."""
        log_debug("Reproduciendo sonido de advertencia") 
        self._play_async('warning')
    
    def set_enabled(self, enabled):
        """Enable or disable sound notifications.
        
        Args:
            enabled (bool): Whether to enable sound notifications
        """
        self.enabled = enabled
        log_debug(f"Sonidos {'habilitados' if enabled else 'deshabilitados'}")
    
    def is_enabled(self):
        """Return whether sound notifications are enabled.
        
        Returns:
            bool: True if sounds are enabled
        """
        return self.enabled


# Global sound manager instance
sound_manager = SoundManager()


# Helper functions for use from any module
def play_success_sound():
    """Play success notification sound."""
    sound_manager.play_success()


def play_error_sound():
    """Play error notification sound."""
    sound_manager.play_error()


def play_warning_sound():
    """Play warning notification sound."""
    sound_manager.play_warning()


def set_sounds_enabled(enabled):
    """Enable or disable sound notifications.
    
    Args:
        enabled (bool): Whether to enable sounds
    """
    sound_manager.set_enabled(enabled)


def are_sounds_enabled():
    """Check if sound notifications are enabled.
    
    Returns:
        bool: True if sounds are enabled
    """
    return sound_manager.is_enabled()