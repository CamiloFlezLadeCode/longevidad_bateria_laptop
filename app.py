# HERRAMIENTA PARA ACCEDER AL ESTADO DE LA BATERÍA DE LA LAPTOP
import psutil
# HERRAMIENTA PARA MOSTRAR NOTIFICACIONES
from notifypy import Notify
# HERRAMIENTA PARA MANEJAR ESPERAS EN LA EJECUCIÓN
import time
# HARRAMIENTA PARA EL MANEJO DE FECHAS
from datetime import datetime
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

load_dotenv()  # Carga las variables de entorno del archivo .env

def enviar_sms(porcentaje_bateria):
    # Se carga la configuración para interactuar con la api twilio
    # Configuración (obtén estos datos en twilio.com/console)
    account_sid = os.environ.get("SID_CUENTA_TWILIO")
    auth_token = os.environ.get("TOKEN_AUTENTICACION_TWILIO")
    twilio_number = os.environ.get("NUMERO_PUBLICO_TWILIO")  # Número proporcionado por Twilio
    recipient_number = os.environ.get("NUMERO_DESTINATARIO_SMS")
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"""
            🔋 BATERÍA CARGADA AL {porcentaje_bateria}%\n---------------------------------------------\nPor favor desconecte el cargador 😊
        """,
        from_=twilio_number,
        to=recipient_number,  # Número destino (con código de país)
    )

    print(f"Mensaje SMS enviado. SID: {message.sid}")


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
    if porcentaje >= 100 and cargando:
    # if porcentaje >= 10:
        global contador
        contador += 1
        NOTIFY_PY_MULTIPLATAFORMA(
            f"Batería Cargada al {porcentaje}%", "Por favor desconecte el cargador 😊"
        )
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS)

        if contador == 1:
            enviar_correo(porcentaje)
            enviar_sms(porcentaje)
            contador = 0

    # Console output (opcional, puede eliminarse para ahorrar energía)
    fecha_hora = datetime.now().strftime("%d/%m/%Y %I:%M %p")
    print(
        f"¿Cargando?: {'Sí' if cargando else 'No'} - Batería: {porcentaje}% - Fecha: [ {fecha_hora} ]",
        flush=True,
    )


# --- Optimización Principal: Bucle con bajo consumo ---
if __name__ == "__main__":
    try:
        while True:
            verificar_bateria()
            time.sleep(10)  # Mantén los 10 segundos
    except KeyboardInterrupt:
        print("\nMonitor de batería detenido.")
