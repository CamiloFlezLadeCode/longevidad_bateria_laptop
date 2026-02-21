# longevidad_bateria_laptop
Aplicación en Python para ayudar con la longevidad de la batería de la laptop. Analiza constantemente el estado de la batería, si está cargando y está al 100%, (muestra notificación en laptop, envía correo electrónico y envía mensaje de texto SMS).

# Pasos comando para instalar dependencias
pip install -r requirements.txt

# Comando para crear/generar .exe del script
pyinstaller --onefile --windowed --icon=battery_78337.ico -n "1_Verificar_Estado_Bateria" app.py
NOTA: Luego de construir el .exe, la carpeta icons debe estar en la raíz donde se ubique el .exe