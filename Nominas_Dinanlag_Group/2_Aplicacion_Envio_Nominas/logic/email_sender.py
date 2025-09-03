import os
import smtplib
import logging
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import pikepdf
import fitz  # PyMuPDF


def enviar_nominas_worker(
    pdf_path, tareas, config, status_callback, progress_callback
):
    """Worker que procesa y envía las nóminas en un hilo separado."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    logging.info("Iniciando el proceso de envío de nóminas.")
    email_origen = ""
    try:
        email_origen = config.get('Email', 'email_origen')
        password = config.get('Email', 'password')
        
        if not email_origen or not password:
            raise ValueError("Credenciales de email no configuradas.")

        servidor_smtp = "smtp.gmail.com"
        puerto_smtp = 587
        
        server = smtplib.SMTP(servidor_smtp, puerto_smtp)
        server.starttls()
        server.login(email_origen, password)

        doc_maestro = fitz.open(pdf_path)
        tareas_a_enviar = [t for t in tareas if t['status'] == '✅ OK']
        # Ordenar por número de página para procesar de arriba hacia abajo
        tareas_a_enviar.sort(key=lambda x: x['pagina'])
        logging.info(f"Se enviarán {len(tareas_a_enviar)} nóminas.")
        
        output_dir = "nominas_individuales"
        os.makedirs(output_dir, exist_ok=True)

        for i, tarea in enumerate(tareas_a_enviar):
            nombre = tarea['nombre']
            nif = tarea['nif']
            email_destino = tarea['email']
            
            print(f"DEBUG EMAIL: Procesando {i+1}/{len(tareas_a_enviar)}: {nombre} (página {tarea['pagina']}) -> {email_destino}")
            logging.info(
                f"Procesando {i+1}/{len(tareas_a_enviar)}: "
                f"{nombre} ({email_destino})"
            )
            
            try:
                status_callback(f"pagina_{tarea['pagina']}", "Procesando...", "processing")
                
                # 1. Extraer y guardar PDF individual
                doc_individual = fitz.open()
                doc_individual.insert_pdf(
                    doc_maestro, from_page=tarea['pagina'] - 1,
                    to_page=tarea['pagina'] - 1)
                
                temp_pdf_path = os.path.join(output_dir, f"temp_{nif}.pdf")
                doc_individual.save(temp_pdf_path)
                doc_individual.close()

                # 2. Encriptar el PDF
                pdf_encriptado_path = os.path.join(
                    output_dir, f"nomina_{nombre.replace(' ', '_')}.pdf"
                )
                with pikepdf.open(temp_pdf_path) as pdf:
                    pdf.save(
                        pdf_encriptado_path,
                        encryption=pikepdf.Encryption(owner=nif, user=nif, R=4)
                    )
                os.remove(temp_pdf_path)

                # 3. Enviar por correo
                msg = MIMEMultipart()
                msg['From'] = email_origen
                msg['To'] = email_destino
                msg['Subject'] = (
                    f"Tu nómina de {datetime.now().strftime('%B %Y')}")
                
                cuerpo = (
                    f"Hola {nombre},\n\nAdjuntamos tu nómina. La contraseña "
                    "para abrir el archivo es tu NIF.\n\nSaludos."
                )
                msg.attach(MIMEText(cuerpo, 'plain'))

                with open(pdf_encriptado_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename= {os.path.basename(pdf_encriptado_path)}"
                )
                msg.attach(part)
                
                server.send_message(msg)
                os.remove(pdf_encriptado_path)
                status_callback(f"pagina_{tarea['pagina']}", "Enviado", "sent")
                logging.info(f"Correo enviado a {email_destino}")
                
            except Exception as e:
                status_callback(f"pagina_{tarea['pagina']}", f"Error: {e}", "error")
            
            progress_callback((i + 1) / len(tareas_a_enviar) * 100)

        server.quit()
        logging.info("Proceso de envío de nóminas finalizado.")
    except Exception as e:
        status_callback("error_general", f"Error General: {e}", "error")
    finally:
        progress_callback(-1)
