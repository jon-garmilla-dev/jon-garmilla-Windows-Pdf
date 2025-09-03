"""
Módulo principal para el envío de nóminas por email - Version refactorizada.
"""
import os
import smtplib
import ssl
import time
import socket
import shutil
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pikepdf
import fitz  # PyMuPDF

from .formato_archivos import generar_nombre_archivo
from .email_templates import generar_asunto_personalizado, generar_cuerpo_personalizado
from .email_reports import generar_reporte_final
from utils.logger import log_info, log_error, log_warning, log_debug


def validar_email_basico(email):
    """Validación básica de formato de email."""
    if not email or not isinstance(email, str):
        return False
    
    email = email.strip().lower()
    
    # Verificaciones básicas
    if '@' not in email or '.' not in email:
        return False
        
    # Verificar que no empiece o termine con caracteres especiales
    if email.startswith(('@', '.', '-', '_')) or email.endswith(('.', '-', '_')):
        return False
        
    # Verificar longitud razonable
    if len(email) < 5 or len(email) > 100:
        return False
        
    # Verificar caracteres válidos (básico)
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def generar_estadisticas_envio(tareas):
    """Genera estadísticas detalladas de las tareas a procesar."""
    stats = {
        'total_validadas': len([t for t in tareas if t['status'] == '[OK]']),
        'total_errores': len([t for t in tareas if t['status'].startswith('[ERROR]')]),
        'total_warnings': len([t for t in tareas if t['status'].startswith('[ADVERTENCIA]')]),
        'emails_invalidos': 0,
        'emails_duplicados': 0
    }
    
    # Analizar emails
    emails_vistos = set()
    for tarea in tareas:
        if tarea['status'] == '[OK]':
            email = tarea.get('email', '').strip().lower()
            
            if not validar_email_basico(email):
                stats['emails_invalidos'] += 1
            
            if email in emails_vistos:
                stats['emails_duplicados'] += 1
            else:
                emails_vistos.add(email)
    
    return stats


class RobustEmailSender:
    """Cliente SMTP robusto con reintentos, timeouts y manejo de errores."""
    
    def __init__(self, config):
        self.config = config
        self.servidor_smtp = config.get('SMTP', 'servidor', fallback='smtp.gmail.com')
        self.puerto_smtp = int(config.get('SMTP', 'puerto', fallback='587'))
        self.timeout = int(config.get('SMTP', 'timeout', fallback='30'))
        self.max_reintentos = int(config.get('SMTP', 'max_reintentos', fallback='3'))
        self.delay_entre_emails = float(config.get('SMTP', 'delay_segundos', fallback='1.0'))
        self.server = None
        self.conexiones_fallidas = 0
        
    def conectar(self, email_origen, password):
        """Establece conexión SMTP con reintentos."""
        for intento in range(self.max_reintentos):
            try:
                log_info(f"Conectando a {self.servidor_smtp}:{self.puerto_smtp} (intento {intento + 1})")
                
                # Configurar timeout a nivel socket
                socket.setdefaulttimeout(self.timeout)
                
                self.server = smtplib.SMTP(self.servidor_smtp, self.puerto_smtp, timeout=self.timeout)
                self.server.set_debuglevel(0)  # 0=sin debug, 1=debug básico, 2=debug completo
                
                log_info("Iniciando TLS...")
                context = ssl.create_default_context()
                self.server.starttls(context=context)
                
                log_info("Autenticando...")
                self.server.login(email_origen, password)
                
                log_info("[OK] Conexión SMTP establecida exitosamente")
                self.conexiones_fallidas = 0
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                log_error(f"[ERROR] Error de autenticación: {e}")
                log_error("Verificar credenciales de email y contraseñas de aplicación")
                return False
                
            except smtplib.SMTPServerDisconnected as e:
                log_warning(f"[ADVERTENCIA] Servidor desconectado (intento {intento + 1}): {e}")
                
            except socket.timeout as e:
                log_warning(f"[ADVERTENCIA] Timeout de conexión (intento {intento + 1}): {e}")
                
            except socket.gaierror as e:
                log_error(f"[ERROR] Error de DNS/red: {e}")
                return False
                
            except Exception as e:
                log_warning(f"[ADVERTENCIA] Error de conexión (intento {intento + 1}): {type(e).__name__}: {e}")
            
            # Backoff exponencial entre reintentos
            if intento < self.max_reintentos - 1:
                delay = (2 ** intento) * 2  # 2, 4, 8 segundos
                log_info(f"Esperando {delay}s antes del siguiente intento...")
                time.sleep(delay)
        
        log_error(f"[ERROR] Failed to connect after {self.max_reintentos} attempts")
        self.conexiones_fallidas += 1
        return False
    
    def enviar_email(self, msg, email_destino, max_reintentos=None):
        """Envía un email con reintentos automáticos."""
        if max_reintentos is None:
            max_reintentos = self.max_reintentos
            
        for intento in range(max_reintentos):
            try:
                # Verificar conexión
                if not self.server:
                    raise smtplib.SMTPServerDisconnected("No hay conexión activa")
                
                # Enviar mensaje
                self.server.send_message(msg)
                
                # Rate limiting - pausa entre emails
                if self.delay_entre_emails > 0:
                    time.sleep(self.delay_entre_emails)
                    
                return True
                
            except smtplib.SMTPServerDisconnected as e:
                log_warning(f"[ADVERTENCIA] Servidor desconectado durante envío (intento {intento + 1}): {e}")
                # Intentar reconectar
                email_origen = self.config.get('Email', 'email_origen')
                password = self.config.get('Email', 'password')
                if self.conectar(email_origen, password):
                    continue  # Reintentar envío
                else:
                    return False
                    
            except smtplib.SMTPRecipientsRefused as e:
                log_error(f"[ERROR] Email rechazado por el servidor: {email_destino} - {e}")
                return False  # No reintentar, email inválido
                
            except smtplib.SMTPDataError as e:
                log_error(f"[ERROR] Error de datos SMTP: {e}")
                return False  # No reintentar, problema con el mensaje
                
            except socket.timeout as e:
                log_warning(f"[ADVERTENCIA] Timeout enviando email (intento {intento + 1}): {e}")
                
            except Exception as e:
                log_warning(f"[ADVERTENCIA] Error enviando email (intento {intento + 1}): {type(e).__name__}: {e}")
            
            # Pausa antes del siguiente intento
            if intento < max_reintentos - 1:
                delay = min((2 ** intento), 10)  # Max 10 segundos
                log_info(f"Esperando {delay}s antes de reintentar envío...")
                time.sleep(delay)
        
        log_error(f"[ERROR] Failed to send email to {email_destino} after {max_reintentos} attempts")
        return False
    
    def cerrar(self):
        """Cierra la conexión SMTP de forma segura."""
        if self.server:
            try:
                self.server.quit()
                log_info("[OK] Conexión SMTP cerrada correctamente")
            except:
                try:
                    self.server.close()
                except:
                    pass
            finally:
                self.server = None


def crear_mensaje_email(config, email_origen, email_destino, nombre, apellidos, pdf_path):
    """Crea el mensaje de email con plantillas personalizadas."""
    msg = MIMEMultipart()
    msg['From'] = email_origen
    msg['To'] = email_destino
    
    # Usar plantillas personalizadas
    msg['Subject'] = generar_asunto_personalizado(config, nombre, apellidos)
    cuerpo_mensaje = generar_cuerpo_personalizado(config, nombre, apellidos)
    
    msg.attach(MIMEText(cuerpo_mensaje, 'plain'))
    
    # Adjuntar PDF
    with open(pdf_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
    
    encoders.encode_base64(part)
    part.add_header(
        'Content-Disposition',
        f'attachment; filename="{os.path.basename(pdf_path)}"'
    )
    msg.attach(part)
    
    return msg


def procesar_pdf_individual(doc_maestro, tarea, output_dir, config):
    """Procesa y guarda un PDF individual encriptado."""
    nombre = tarea['nombre']
    nif = tarea['nif']
    
    # 1. Extraer PDF individual
    doc_individual = fitz.open()
    doc_individual.insert_pdf(
        doc_maestro, from_page=tarea['pagina'] - 1,
        to_page=tarea['pagina'] - 1)
    
    temp_pdf_path = os.path.join(output_dir, f"temp_{nif}.pdf")
    doc_individual.save(temp_pdf_path)
    doc_individual.close()

    # 2. Generar nombre de archivo personalizado  
    plantilla_archivo = config.get('Formato', 'archivo_nomina', 
                                  fallback='{nombre}_Nomina_{mes}_{año}.pdf')
    
    # Obtener apellidos de la tarea
    apellido_empleado = tarea.get('apellidos', '')
    if not apellido_empleado and ' ' in nombre:
        # Si no hay apellido separado, intentar separar del nombre completo
        partes = nombre.strip().split(' ', 1)
        nombre_empleado = partes[0]
        apellido_empleado = partes[1] if len(partes) > 1 else ''
    else:
        nombre_empleado = nombre
    
    nombre_archivo = generar_nombre_archivo(plantilla_archivo, nombre_empleado, apellido_empleado)
    
    pdf_encriptado_path = os.path.join(output_dir, nombre_archivo)
    
    # 3. Encriptar PDF
    password_autor = config.get('PDF', 'password_autor', fallback='')
    owner_password = password_autor if password_autor else nif
    
    log_debug(f"Encriptando PDF para {nombre}")
    with pikepdf.open(temp_pdf_path) as pdf:
        pdf.save(
            pdf_encriptado_path,
            encryption=pikepdf.Encryption(owner=owner_password, user=nif, R=4)
        )
    os.remove(temp_pdf_path)
    
    return pdf_encriptado_path


def enviar_nominas_worker(pdf_path, tareas, config, status_callback, progress_callback, stop_event=None):
    """Worker que procesa y envía las nóminas en un hilo separado."""
    log_info("Iniciando el proceso de envío de nóminas.")
    
    # IMPORTANTE: Siempre recargar configuración para asegurar descifrado
    from .settings import load_settings
    config_descifrada = load_settings()
    
    # Estadísticas de envío
    stats = {
        'total': 0,
        'enviados': 0, 
        'errores': 0,
        'saltados': 0,
        'errores_lista': []
    }
    
    email_sender = None
    try:
        email_origen = config_descifrada.get('Email', 'email_origen')
        password = config_descifrada.get('Email', 'password')
        
        log_info(f"Email configurado: {email_origen}")
        log_info("Configuración cargada y descifrada correctamente")
        
        if not email_origen or not password:
            log_error("[ERROR] Credenciales de email no configuradas")
            raise ValueError("[ERROR] Credenciales de email no configuradas.")

        # Inicializar cliente robusto de email
        email_sender = RobustEmailSender(config_descifrada)
        
        # Establecer conexión con reintentos automáticos
        log_info("Estableciendo conexión SMTP...")
        
        if not email_sender.conectar(email_origen, password):
            log_error("[ERROR] Falló la conexión SMTP después de reintentos")
            raise ConnectionError("[ERROR] No se pudo establecer conexión SMTP después de varios intentos")
        log_info("[OK] Conexión SMTP establecida correctamente")

        # Análisis previo de las tareas
        pre_stats = generar_estadisticas_envio(tareas)
        log_info("ANÁLISIS PREVIO:")
        log_info(f"   [OK] Validadas para envío: {pre_stats['total_validadas']}")
        log_info(f"   [ERROR] Con errores: {pre_stats['total_errores']}")
        log_info(f"   [ADVERTENCIA] Con warnings: {pre_stats['total_warnings']}")
        if pre_stats['emails_invalidos'] > 0:
            log_warning(f"   [ADVERTENCIA] Emails con formato inválido: {pre_stats['emails_invalidos']}")
        if pre_stats['emails_duplicados'] > 0:
            log_warning(f"   [ADVERTENCIA] Emails duplicados detectados: {pre_stats['emails_duplicados']}")

        doc_maestro = fitz.open(pdf_path)
        tareas_a_enviar = [t for t in tareas if t['status'] == '[OK]']
        # Ordenar por número de página para procesar de arriba hacia abajo
        tareas_a_enviar.sort(key=lambda x: x['pagina'])
        
        stats['total'] = len(tareas_a_enviar)
        log_info(f"Iniciando procesamiento de {stats['total']} nóminas.")
        
        # Crear estructura organizada por mes/año
        base_dir = config_descifrada.get('Carpetas', 'salida', fallback='nominas_individuales')
        fecha_actual = datetime.now()
        
        # Carpeta principal: nominas_2025_09/
        carpeta_mes = os.path.join(base_dir, f"nominas_{fecha_actual.year}_{fecha_actual.month:02d}")
        
        # Subcarpeta para PDFs: nominas_2025_09/pdfs_individuales/
        output_dir = os.path.join(carpeta_mes, "pdfs_individuales")
        os.makedirs(output_dir, exist_ok=True)
        
        # Guardar carpeta para el reporte
        stats['carpeta_mes'] = carpeta_mes
        stats['carpeta_pdfs'] = output_dir
        
        log_info(f"📁 Estructura creada: {carpeta_mes}")
        log_info(f"📁 PDFs se guardarán en: {output_dir}")
        
        # Copiar PDF original a la carpeta del mes
        try:
            nombre_pdf_original = os.path.basename(pdf_path)
            destino_pdf_original = os.path.join(carpeta_mes, nombre_pdf_original)
            shutil.copy2(pdf_path, destino_pdf_original)
            log_info(f"PDF original copiado: {destino_pdf_original}")
        except Exception as e:
            log_error(f"[ERROR] Error al copiar PDF original: {e}")

        # Procesar cada nómina con recuperación de errores
        for i, tarea in enumerate(tareas_a_enviar):
            # Verificar si se debe cancelar el proceso
            if stop_event and stop_event.is_set():
                log_info("[CANCELADO] Proceso de envío cancelado por el usuario.")
                status_callback("proceso_cancelado", "Proceso cancelado", "cancelled")
                break
                
            nombre = tarea['nombre']
            nif = tarea['nif']
            email_destino = tarea['email']
            apellidos_empleado = tarea.get('apellidos', '')
            
            log_info(f"Procesando {i+1}/{stats['total']}: {nombre} -> {email_destino}")
            
            tarea_exitosa = False
            error_msg = ""
            
            try:
                status_callback(f"pagina_{tarea['pagina']}", "Procesando PDF...", "processing")
                
                # 1. Validar email antes de procesar
                if not validar_email_basico(email_destino):
                    raise ValueError(f"Formato de email inválido: {email_destino}")
                
                # 2. Procesar PDF individual
                pdf_encriptado_path = procesar_pdf_individual(doc_maestro, tarea, output_dir, config_descifrada)
                
                # 3. Preparar email
                status_callback(f"pagina_{tarea['pagina']}", "Enviando email...", "processing")
                
                msg = crear_mensaje_email(config_descifrada, email_origen, email_destino, 
                                        nombre, apellidos_empleado, pdf_encriptado_path)
                
                # 4. Enviar con reintentos automáticos
                envio_exitoso = email_sender.enviar_email(msg, email_destino)
                if envio_exitoso:
                    # Éxito - MANTENER el PDF para archivo
                    status_callback(f"pagina_{tarea['pagina']}", "SUCCESS", "sent")
                    stats['enviados'] += 1
                    log_info(f"Email enviado exitosamente a {email_destino} (total enviados: {stats['enviados']})")
                    tarea_exitosa = True
                else:
                    # Error en envío (ya reintentado automáticamente)
                    error_msg = f"Fallo en envío después de reintentos"
                    stats['errores'] += 1
                    # Mantener PDF para inspección manual
                    log_error(f"Email fallido a {email_destino} (total errores: {stats['errores']})")
                    
                    # Agregar a lista de errores
                    stats['errores_lista'].append({
                        'nombre': nombre,
                        'email': email_destino,
                        'error': error_msg
                    })
                
            except Exception as e:
                # Error en procesamiento del PDF o preparación del email
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                stats['errores'] += 1
                log_error(f"[ERROR] Error procesando {nombre}: {error_msg}")
                log_debug("Stack trace completo:", exc_info=True)
                
                # Limpiar archivos temporales en caso de error
                try:
                    if 'pdf_encriptado_path' in locals() and os.path.exists(pdf_encriptado_path):
                        os.remove(pdf_encriptado_path)
                except:
                    pass
            
            # Actualizar estado final
            if not tarea_exitosa:
                status_callback(f"pagina_{tarea['pagina']}", f"ERROR: {error_msg}", "error")
                # Si no se agregó ya a la lista de errores, agregarlo ahora
                if not any(err['email'] == email_destino and err['nombre'] == nombre for err in stats['errores_lista']):
                    stats['errores_lista'].append({
                        'nombre': nombre,
                        'email': email_destino,
                        'error': error_msg
                    })
            
            # Actualizar progreso
            progress_callback((i + 1) / stats['total'] * 100)

        # Cerrar conexión de forma segura
        if email_sender:
            email_sender.cerrar()
        
        # Cerrar documento PDF maestro
        if doc_maestro:
            doc_maestro.close()
        
        # Resumen final
        log_info("=" * 50)
        log_info("RESUMEN DEL ENVÍO:")
        log_info(f"   Total procesadas: {stats['total']}")
        log_info(f"   [OK] Enviadas exitosamente: {stats['enviados']}")
        log_info(f"   [ERROR] Con errores: {stats['errores']}")
        if stats['errores'] > 0:
            log_info("   Errores encontrados:")
            for error_info in stats['errores_lista'][:5]:  # Mostrar solo primeros 5
                log_info(f"      • {error_info['nombre']}: {error_info['error']}")
            if len(stats['errores_lista']) > 5:
                log_info(f"      ... y {len(stats['errores_lista']) - 5} errores más")
        
        tasa_exito = (stats['enviados'] / stats['total'] * 100) if stats['total'] > 0 else 0
        log_info(f"   📈 Tasa de éxito: {tasa_exito:.1f}%")
        log_info("=" * 50)
        
        # Generar reporte final con TODAS las tareas originales (para mostrar PENDIENTES)
        generar_reporte_final(stats, tareas, config_descifrada)
        
        # Pasar estadísticas finales al callback
        log_info(f"ENVIANDO ESTADÍSTICAS FINALES: enviados={stats['enviados']}, errores={stats['errores']}, total={stats['total']}")
        status_callback("estadisticas_finales", "", "completed", stats)
        
        if stats['enviados'] > 0:
            log_info("[OK] Proceso de envío de nóminas completado.")
        else:
            log_warning("[ADVERTENCIA] No se enviaron nóminas exitosamente.")
            
    except Exception as e:
        log_error(f"[ERROR] Error crítico en el proceso: {type(e).__name__}: {e}")
        log_debug("Stack trace crítico:", exc_info=True)
        status_callback("error_general", f"Error crítico: {str(e)[:100]}", "error")
        
        # Intentar cerrar conexiones en caso de error
        try:
            if email_sender:
                email_sender.cerrar()
        except:
            pass
            
    finally:
        # Asegurar que se complete el progreso
        progress_callback(-1)