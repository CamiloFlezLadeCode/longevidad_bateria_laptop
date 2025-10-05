# HERRAMIENTA PARA ACCEDER AL ESTADO DE LA BATERÍA DE LA LAPTOP
import psutil

# HERRAMIENTA PARA MOSTRAR NOTIFICACIONES
from notifypy import Notify

# HERRAMIENTA PARA MANEJAR ESPERAS EN LA EJECUCIÓN
import time

# HARRAMIENTA PARA EL MANEJO DE FECHAS
from datetime import datetime, timedelta

# HERRAMIENTA PARA GENERAR/EMITIR SONIDO
import winsound

# HERRAMIENTAS PARA ENVIAR CORREO
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# HERRAMIENTAS PARA ENVIAR MENSAJE DE TEXTO SMS / CON LA API TWILIO
from twilio.rest import Client
import json

# HERRAMIENTAS PARA CAPTURAR VARIABLES DE ENTORNO
from dotenv import load_dotenv
import os

# HERRAMIENTA PARA TRABAJAR CON LECTURA DE ARCHIVOS Y RECONOCER AUTOMÁTICAMENTE LA CODIFICACIÓN
import chardet
import re

# HERRAMIENTA PARA TRABAJAR CON ZONA HORARIA
import pytz

load_dotenv()  # Carga las variables de entorno del archivo .env


def enviar_sms(porcentaje_bateria):
    client = None  # Inicializamos client para el bloque finally
    try:
        # 1. Validación de variables de entorno
        account_sid = os.environ.get("SID_CUENTA_TWILIO")
        auth_token = os.environ.get("TOKEN_AUTENTICACION_TWILIO")
        twilio_number = os.environ.get("NUMERO_PUBLICO_TWILIO")
        recipient_number = os.environ.get("NUMERO_DESTINATARIO_SMS")

        if not all([account_sid, auth_token, twilio_number, recipient_number]):
            raise ValueError("Faltan variables de entorno requeridas para Twilio")

        print(f"Intentando enviar SMS a: {recipient_number}")

        # 2. Creamos el cliente
        client = Client(account_sid, auth_token)

        # 3. Enviamos el mensaje (versión más limpia del body)
        message = client.messages.create(
            body=f"🔋 BATERÍA CARGADA AL {porcentaje_bateria}%\n"
            "---------------------------------------------\n"
            "Por favor desconecte el cargador 😊",
            from_=twilio_number,
            to=recipient_number,
        )

        print(f"SMS enviado. SID: {message.sid}")
        print(f"Estado del mensaje SMS. STATUS: {message.status}")
        print(
            f"Estado: https://console.twilio.com/us1/monitor/logs/message-logs/{message.sid}"
        )

        return True  # Indicador de éxito

    except Exception as e:
        print(f"Error al enviar SMS: {str(e)}")
        return False  # Indicador de fallo
    finally:
        pass


def enviar_correo(nivel_de_bateria):
    # Configuración del servidor SMTP (ejemplo para Gmail)
    smtp_server = os.environ.get("SERVIDOR_SMTP")
    smtp_port = os.environ.get("PUERTO_SMTP")
    remitente = os.environ.get("REMITENTE")
    password = os.environ.get("CONTRASENA_DE_APLICACIONES")
    # Destinatario y mensaje
    destinatario = os.environ.get("CORREO_DESTINATARIO")
    asunto = "🔋 ¡ALERTA! Batería de la laptop completamente cargada"
    # cuerpo = "Hola, esto es un correo enviado usando Python."
    cuerpo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                    color: #333;
                }}
                .container {{
                    background-color: #ffffff;
                    border-radius: 10px;
                    padding: 20px;
                    max-width: 600px;
                    margin: 0 auto;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 15px;
                    border-radius: 8px 8px 0 0;
                    text-align: center;
                    font-size: 24px;
                    font-weight: bold;
                }}
                .content {{
                    padding: 20px;
                    text-align: center;
                }}
                .battery-icon {{
                    font-size: 50px;
                    margin-bottom: 20px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 12px;
                    text-align: center;
                    color: #777;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    ¡Batería cargada al {nivel_de_bateria}%!
                </div>
                <div class="content">
                    <div class="battery-icon">🔋</div>
                    <h2>¡La laptop está lista para usar!</h2>
                    <p>La batería ha alcanzado su carga máxima. Desconecta el cargador para optimizar su vida útil.</p>
                </div>
                <div class="footer">
                    Este mensaje fue generado automáticamente por tu sistema de monitoreo.
                </div>
            </div>
        </body>
        </html>
    """

    # Crear el mensaje
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = asunto
    # mensaje.attach(MIMEText(cuerpo, "plain"))
    mensaje.attach(MIMEText(cuerpo_html, "html"))

    # Enviar el correo
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Cifrado TLS
        server.login(remitente, password)
        server.sendmail(remitente, destinatario, mensaje.as_string())
        print("Correo enviado correctamente.")
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
    finally:
        server.quit()


def limpiar_log():
    # Ruta del archivo log
    input_file = "SALIDA.log"

    # Zona horaria de Colombia
    tz_colombia = pytz.timezone("America/Bogota")

    # Fecha actual en Colombia
    now = datetime.now(tz_colombia)

    # Fecha límite (2 días atrás)
    limit_date = now - timedelta(days=2)

    # Expresión regular para capturar la fecha dentro de corchetes
    pattern = re.compile(
        r"Fecha:\s*\[\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[APM]{2})\s*\]"
    )

    # Detectar encoding del archivo
    with open(input_file, "rb") as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        encoding_detected = result["encoding"]

    lines_to_keep = []
    keep_block = False  # bandera para saber si estamos en rango válido

    # Abrir el archivo ya con el encoding correcto
    with open(input_file, "r", encoding=encoding_detected) as f:
        for line in f:
            match = pattern.search(line)
            if match:
                try:
                    # Parsear la fecha encontrada
                    log_date = datetime.strptime(match.group(1), "%d/%m/%Y %I:%M %p")
                    log_date = tz_colombia.localize(log_date)

                    # Si está dentro del rango, activamos bandera y guardamos
                    if log_date >= limit_date:
                        keep_block = True
                        lines_to_keep.append(line)
                    else:
                        keep_block = False
                except ValueError:
                    pass
            else:
                # Si no hay fecha y la bandera está activa, conservamos
                # if keep_block:
                #     lines_to_keep.append(line)
                if keep_block and line.strip():
                    lines_to_keep.append(line.rstrip() + "\n")

    # ⚠️ Sobrescribir el mismo archivo con el resultado
    with open(input_file, "w", encoding=encoding_detected) as f:
        f.writelines(lines_to_keep)

    print(f"Archivo limpio generado y sobrescrito: {input_file}")


def ejecutar_limpieza_diaria(ultima_limpieza_file):
    hoy = datetime.now().date()

    # Si no existe el archivo de control, crearlo
    if not os.path.exists(ultima_limpieza_file):
        with open(ultima_limpieza_file, "w") as f:
            f.write(str(hoy))
        limpiar_log()
        return

    # Leer la última fecha de limpieza
    with open(ultima_limpieza_file, "r") as f:
        ultima_fecha = f.read().strip()

    try:
        ultima_fecha = datetime.strptime(ultima_fecha, "%Y-%m-%d").date()
    except ValueError:
        ultima_fecha = None

    # Si no se limpió hoy, ejecutamos la limpieza
    if ultima_fecha != hoy:
        limpiar_log()
        with open(ultima_limpieza_file, "w") as f:
            f.write(str(hoy))


def NOTIFY_PY_MULTIPLATAFORMA(Titulo, Mensaje):
    notification = Notify(
        # default_application_name="Great Application",
        default_notification_application_name="ALERTA DE BATERÍA"
    )
    notification.title = Titulo
    notification.message = Mensaje
    notification.icon = r"icons/icons8-full-battery-96.png"
    notification.send()


# def guardar_log(porcentaje, cargando):
#     """Optimización: Abre el archivo una sola vez al inicio y usa 'write' en modo buffer."""
#     Cargando = 'Sí' if cargando else 'No'
#     fecha_hora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
#     with open("bateria_log.log", "a", buffering=1, encoding="utf-8") as log_file:  # buffering=1 (line-buffered)
#         log_file.write(f"Batería: {porcentaje}% - ¿Cargando?: {Cargando} => [ {fecha_hora} ]\n")

contador = 0


def verificar_bateria():
    """Optimización: Reduce llamadas innecesarias y simplifica condicionales."""
    battery = psutil.sensors_battery()
    if not battery:
        print("No hay información de la batería disponible.")
        return

    porcentaje = battery.percent
    cargando = battery.power_plugged
    # guardar_log(porcentaje, cargando)

    # Solo notificar si es 100% y está cargando (evita múltiples notificaciones)
    # if porcentaje >= 10:
    if porcentaje >= 100 and cargando:
        global contador
        contador += 1
        NOTIFY_PY_MULTIPLATAFORMA(
            f"Batería Cargada al {porcentaje}%", "Por favor desconecte el cargador 😊"
        )
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

        if contador == 5:
            enviar_correo(porcentaje)
            enviar_sms(porcentaje)
            contador = 0

    # Console output (opcional, puede eliminarse para ahorrar energía)
    fecha_hora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    print(
        f"¿Cargando?: {'Sí' if cargando else 'No'} - Batería: {porcentaje}% - Fecha: [ {fecha_hora} ]",
        flush=True,
    )

    ejecutar_limpieza_diaria(os.environ.get("NOMBRE_ARCHIVO_ULTIMA_LIMPIEZ_LOG"))


# --- Optimización Principal: Bucle con bajo consumo ---
if __name__ == "__main__":
    try:
        while True:
            verificar_bateria()
            time.sleep(10)  # Mantén los 10 segundos
    except KeyboardInterrupt:
        print("\nMonitor de batería detenido.")
