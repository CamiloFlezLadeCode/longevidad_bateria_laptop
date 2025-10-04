# '''
# HACE LA LIMPIEZA PERO LA ALMACENA EN UN ARCHIVO APARTE
# '''
# import re
# from datetime import datetime, timedelta
# import pytz
# import chardet

# def limpiar_log():
#     # Ruta del archivo log
#     input_file = "SALIDA.log"
#     output_file = "archivo_limpio.log"

#     # Zona horaria de Colombia
#     tz_colombia = pytz.timezone("America/Bogota")

#     # Fecha actual en Colombia
#     now = datetime.now(tz_colombia)

#     # Fecha límite (3 días atrás)
#     limit_date = now - timedelta(days=3)

#     # Expresión regular para capturar la fecha dentro de corchetes
#     pattern = re.compile(r"Fecha:\s*\[\s*(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}\s+[APM]{2})\s*\]")

#     # Detectar encoding del archivo
#     with open(input_file, "rb") as f:
#         rawdata = f.read()
#         result = chardet.detect(rawdata)
#         encoding_detected = result["encoding"]

#     lines_to_keep = []
#     keep_block = False  # bandera para saber si estamos en rango válido

#     # Abrir el archivo ya con el encoding correcto
#     with open(input_file, "r", encoding=encoding_detected) as f:
#         for line in f:
#             match = pattern.search(line)
#             if match:
#                 try:
#                     # Parsear la fecha encontrada
#                     log_date = datetime.strptime(match.group(1), "%d/%m/%Y %I:%M %p")
#                     log_date = tz_colombia.localize(log_date)

#                     # Si está dentro del rango, activamos bandera y guardamos
#                     if log_date >= limit_date:
#                         keep_block = True
#                         lines_to_keep.append(line)
#                     else:
#                         keep_block = False
#                 except ValueError:
#                     pass
#             else:
#                 # Si no hay fecha y la bandera está activa, conservamos
#                 if keep_block:
#                     lines_to_keep.append(line)

#     # Guardar el nuevo archivo
#     with open(output_file, "w", encoding=encoding_detected) as f:
#         f.writelines(lines_to_keep)

#     print(f"Archivo limpio generado: {output_file}")


# limpiar_log()


"""
HACE LA LIMPIEZA Y LA GUARDA SOBRE EL MISMO ARCHIVO
"""
import re
from datetime import datetime, timedelta
import pytz
import chardet


def limpiar_log():
    # Ruta del archivo log
    input_file = "SALIDA.log"

    # Zona horaria de Colombia
    tz_colombia = pytz.timezone("America/Bogota")

    # Fecha actual en Colombia
    now = datetime.now(tz_colombia)

    # Fecha límite (3 días atrás)
    limit_date = now - timedelta(days=3)

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
                if keep_block:
                    lines_to_keep.append(line)

    # ⚠️ Sobrescribir el mismo archivo con el resultado
    with open(input_file, "w", encoding=encoding_detected) as f:
        f.writelines(lines_to_keep)

    print(f"Archivo limpio generado y sobrescrito: {input_file}")


limpiar_log()
