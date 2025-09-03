import os
import smtplib
import logging
import time
import socket
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pikepdf
import fitz  # PyMuPDF
from .formato_archivos import generar_nombre_archivo


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
        'total_validadas': len([t for t in tareas if t['status'] == '✅ OK']),
        'total_errores': len([t for t in tareas if t['status'].startswith('❌')]),
        'total_warnings': len([t for t in tareas if t['status'].startswith('⚠️')]),
        'emails_invalidos': 0,
        'emails_duplicados': 0
    }
    
    # Analizar emails
    emails_vistos = set()
    for tarea in tareas:
        if tarea['status'] == '✅ OK':
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
                logging.info(f"Conectando a {self.servidor_smtp}:{self.puerto_smtp} (intento {intento + 1})")
                
                # Configurar timeout a nivel socket
                socket.setdefaulttimeout(self.timeout)
                
                self.server = smtplib.SMTP(self.servidor_smtp, self.puerto_smtp, timeout=self.timeout)
                self.server.set_debuglevel(0)  # 0=sin debug, 1=debug básico, 2=debug completo
                
                logging.info("Iniciando TLS...")
                self.server.starttls()
                
                logging.info("Autenticando...")
                self.server.login(email_origen, password)
                
                logging.info("✅ Conexión SMTP establecida exitosamente")
                self.conexiones_fallidas = 0
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logging.error(f"❌ Error de autenticación: {e}")
                logging.error("Verificar credenciales de email y contraseñas de aplicación")
                return False
                
            except smtplib.SMTPServerDisconnected as e:
                logging.warning(f"⚠️  Servidor desconectado (intento {intento + 1}): {e}")
                
            except socket.timeout as e:
                logging.warning(f"⚠️  Timeout de conexión (intento {intento + 1}): {e}")
                
            except socket.gaierror as e:
                logging.error(f"❌ Error de DNS/red: {e}")
                return False
                
            except Exception as e:
                logging.warning(f"⚠️  Error de conexión (intento {intento + 1}): {type(e).__name__}: {e}")
            
            # Backoff exponencial entre reintentos
            if intento < self.max_reintentos - 1:
                delay = (2 ** intento) * 2  # 2, 4, 8 segundos
                logging.info(f"Esperando {delay}s antes del siguiente intento...")
                time.sleep(delay)
        
        logging.error(f"❌ Failed to connect after {self.max_reintentos} attempts")
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
                logging.warning(f"⚠️  Servidor desconectado durante envío (intento {intento + 1}): {e}")
                # Intentar reconectar
                email_origen = self.config.get('Email', 'email_origen')
                password = self.config.get('Email', 'password')
                if self.conectar(email_origen, password):
                    continue  # Reintentar envío
                else:
                    return False
                    
            except smtplib.SMTPRecipientsRefused as e:
                logging.error(f"❌ Email rechazado por el servidor: {email_destino} - {e}")
                return False  # No reintentar, email inválido
                
            except smtplib.SMTPDataError as e:
                logging.error(f"❌ Error de datos SMTP: {e}")
                return False  # No reintentar, problema con el mensaje
                
            except socket.timeout as e:
                logging.warning(f"⚠️  Timeout enviando email (intento {intento + 1}): {e}")
                
            except Exception as e:
                logging.warning(f"⚠️  Error enviando email (intento {intento + 1}): {type(e).__name__}: {e}")
            
            # Pausa antes del siguiente intento
            if intento < max_reintentos - 1:
                delay = min((2 ** intento), 10)  # Max 10 segundos
                logging.info(f"Esperando {delay}s antes de reintentar envío...")
                time.sleep(delay)
        
        logging.error(f"❌ Failed to send email to {email_destino} after {max_reintentos} attempts")
        return False
    
    def cerrar(self):
        """Cierra la conexión SMTP de forma segura."""
        if self.server:
            try:
                self.server.quit()
                logging.info("✅ Conexión SMTP cerrada correctamente")
            except:
                try:
                    self.server.close()
                except:
                    pass
            finally:
                self.server = None


def enviar_nominas_worker(
    pdf_path, tareas, config, status_callback, progress_callback
):
    """Worker que procesa y envía las nóminas en un hilo separado."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info("🚀 Iniciando el proceso de envío de nóminas.")
    
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
        email_origen = config.get('Email', 'email_origen')
        password = config.get('Email', 'password')
        
        if not email_origen or not password:
            raise ValueError("❌ Credenciales de email no configuradas.")

        # Inicializar cliente robusto de email
        email_sender = RobustEmailSender(config)
        
        # Establecer conexión con reintentos automáticos
        if not email_sender.conectar(email_origen, password):
            raise ConnectionError("❌ No se pudo establecer conexión SMTP después de varios intentos")

        # Análisis previo de las tareas
        pre_stats = generar_estadisticas_envio(tareas)
        logging.info(f"📊 ANÁLISIS PREVIO:")
        logging.info(f"   ✅ Validadas para envío: {pre_stats['total_validadas']}")
        logging.info(f"   ❌ Con errores: {pre_stats['total_errores']}")
        logging.info(f"   ⚠️  Con warnings: {pre_stats['total_warnings']}")
        if pre_stats['emails_invalidos'] > 0:
            logging.warning(f"   📧 Emails con formato inválido: {pre_stats['emails_invalidos']}")
        if pre_stats['emails_duplicados'] > 0:
            logging.warning(f"   🔄 Emails duplicados detectados: {pre_stats['emails_duplicados']}")

        doc_maestro = fitz.open(pdf_path)
        tareas_a_enviar = [t for t in tareas if t['status'] == '✅ OK']
        # Ordenar por número de página para procesar de arriba hacia abajo
        tareas_a_enviar.sort(key=lambda x: x['pagina'])
        
        stats['total'] = len(tareas_a_enviar)
        logging.info(f"🚀 Iniciando procesamiento de {stats['total']} nóminas.")
        
        output_dir = config.get('Carpetas', 'salida', fallback='nominas_individuales')
        os.makedirs(output_dir, exist_ok=True)

        # Procesar cada nómina con recuperación de errores
        for i, tarea in enumerate(tareas_a_enviar):
            nombre = tarea['nombre']
            nif = tarea['nif']
            email_destino = tarea['email']
            
            logging.info(
                f"📧 Procesando {i+1}/{stats['total']}: "
                f"{nombre} → {email_destino}"
            )
            
            tarea_exitosa = False
            error_msg = ""
            
            try:
                status_callback(f"pagina_{tarea['pagina']}", "Procesando PDF...", "processing")
                
                # 1. Validar email antes de procesar
                if not validar_email_basico(email_destino):
                    raise ValueError(f"Formato de email inválido: {email_destino}")
                
                # 2. Extraer y guardar PDF individual
                doc_individual = fitz.open()
                doc_individual.insert_pdf(
                    doc_maestro, from_page=tarea['pagina'] - 1,
                    to_page=tarea['pagina'] - 1)
                
                temp_pdf_path = os.path.join(output_dir, f"temp_{nif}.pdf")
                doc_individual.save(temp_pdf_path)
                doc_individual.close()

                # 3. Generar nombre de archivo personalizado  
                plantilla_archivo = config.get('Formato', 'archivo_nomina', 
                                              fallback='{nombre}_Nomina_{mes}_{año}.pdf')
                
                # Intentar obtener apellido si existe en la tarea, sino separar del nombre
                apellido_empleado = tarea.get('apellido', '')
                if not apellido_empleado and ' ' in nombre:
                    # Si no hay apellido separado, intentar separar del nombre completo
                    partes = nombre.strip().split(' ', 1)
                    nombre_empleado = partes[0]
                    apellido_empleado = partes[1] if len(partes) > 1 else ''
                else:
                    nombre_empleado = nombre
                
                nombre_archivo = generar_nombre_archivo(plantilla_archivo, nombre_empleado, apellido_empleado)
                
                pdf_encriptado_path = os.path.join(output_dir, nombre_archivo)
                
                # Usar contraseña de autor si está configurada
                password_autor = config.get('PDF', 'password_autor', fallback='')
                owner_password = password_autor if password_autor else nif
                
                logging.debug(f"Encriptando PDF para {nombre}")
                with pikepdf.open(temp_pdf_path) as pdf:
                    pdf.save(
                        pdf_encriptado_path,
                        encryption=pikepdf.Encryption(owner=owner_password, user=nif, R=4)
                    )
                os.remove(temp_pdf_path)

                # 4. Preparar email
                status_callback(f"pagina_{tarea['pagina']}", "Enviando email...", "processing")
                
                msg = MIMEMultipart()
                msg['From'] = email_origen
                msg['To'] = email_destino
                msg['Subject'] = f"Tu nómina de {datetime.now().strftime('%B %Y')}"
                
                cuerpo = (
                    f"Hola {nombre},\n\n"
                    f"Adjuntamos tu nómina correspondiente a {datetime.now().strftime('%B %Y')}.\n"
                    f"La contraseña para abrir el archivo es tu NIF.\n\n"
                    f"Saludos cordiales."
                )
                msg.attach(MIMEText(cuerpo, 'plain'))

                # Adjuntar PDF encriptado
                with open(pdf_encriptado_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{os.path.basename(pdf_encriptado_path)}"'
                )
                msg.attach(part)
                
                # 5. Enviar con reintentos automáticos
                if email_sender.enviar_email(msg, email_destino):
                    # Éxito
                    os.remove(pdf_encriptado_path)  # Limpiar archivo temporal
                    status_callback(f"pagina_{tarea['pagina']}", "✅ Enviado", "sent")
                    stats['enviados'] += 1
                    logging.info(f"✅ Email enviado exitosamente a {email_destino}")
                    tarea_exitosa = True
                else:
                    # Error en envío (ya reintentado automáticamente)
                    error_msg = f"Fallo en envío después de reintentos"
                    stats['errores'] += 1
                    # Mantener PDF para inspección manual
                    logging.error(f"❌ Email fallido a {email_destino}")
                
            except Exception as e:
                # Error en procesamiento del PDF o preparación del email
                error_msg = f"{type(e).__name__}: {str(e)[:100]}"
                stats['errores'] += 1
                logging.error(f"❌ Error procesando {nombre}: {error_msg}")
                
                # Limpiar archivos temporales en caso de error
                try:
                    if 'temp_pdf_path' in locals() and os.path.exists(temp_pdf_path):
                        os.remove(temp_pdf_path)
                    if 'pdf_encriptado_path' in locals() and os.path.exists(pdf_encriptado_path):
                        os.remove(pdf_encriptado_path)
                except:
                    pass
            
            # Actualizar estado final
            if not tarea_exitosa:
                status_callback(f"pagina_{tarea['pagina']}", f"❌ Error: {error_msg}", "error")
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
        logging.info("=" * 50)
        logging.info("📊 RESUMEN DEL ENVÍO:")
        logging.info(f"   📋 Total procesadas: {stats['total']}")
        logging.info(f"   ✅ Enviadas exitosamente: {stats['enviados']}")
        logging.info(f"   ❌ Con errores: {stats['errores']}")
        if stats['errores'] > 0:
            logging.info("   💥 Errores encontrados:")
            for error_info in stats['errores_lista'][:5]:  # Mostrar solo primeros 5
                logging.info(f"      • {error_info['nombre']}: {error_info['error']}")
            if len(stats['errores_lista']) > 5:
                logging.info(f"      ... y {len(stats['errores_lista']) - 5} errores más")
        
        tasa_exito = (stats['enviados'] / stats['total'] * 100) if stats['total'] > 0 else 0
        logging.info(f"   📈 Tasa de éxito: {tasa_exito:.1f}%")
        logging.info("=" * 50)
        
        # Pasar estadísticas finales al callback
        status_callback("estadisticas_finales", "", "completed", stats)
        
        if stats['enviados'] > 0:
            logging.info("🎉 Proceso de envío de nóminas completado.")
        else:
            logging.warning("⚠️  No se enviaron nóminas exitosamente.")
            
    except Exception as e:
        logging.error(f"❌ Error crítico en el proceso: {type(e).__name__}: {e}")
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
