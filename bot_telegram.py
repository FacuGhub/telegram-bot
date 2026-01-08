import os
import re
import logging
import requests #type: ignore
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

#------------------------------------------
#CONFIGURACION
#------------------------------------------

TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise RuntimeError("No se encontró TELEGRAM_TOKEN")

# ✅ URL NUEVA DEL FORM (ACTUALIZALA)
FORM_URL = "https://docs.google.com/forms/u/0/d/e/1FAIpQLSckmPBAGBwWg07PNL5y31nH9nnYsd6BdUOFUBfHQMAFFRpRuw/formResponse"

#CONFIGURAR LOGGIN PARA VER ERRORES Y ACTIVIDAD DEL BOT
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler("bot_error.log", encoding="utf-8"), #Guarda erores en archivo
        logging.StreamHandler() #Sigue mostrando en consola
        ]
)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)    # opcional

#------------
#FUNCION DEDICADA A PARSEAR Y VALIDAR
#------------

def parsear_mensaje(texto_raw: str) -> dict:
    lineas = [l.strip() for l in texto_raw.splitlines() if l.strip() != ""]

    # Permitimos 7 u 8 líneas (comentarios opcional)
    if len(lineas) not in (7, 8):
        raise ValueError("FORMATO")

    fecha_txt = lineas[0]
    capacitador = lineas[1]
    cadena = lineas[2]
    zona = lineas[3]
    direccion = lineas[4]
    cantidad = lineas[5]
    vendedores_txt = lineas[6]
    comentarios = lineas[7] if len(lineas) == 8 else ""

    # FECHA: DD-MM-YY
    if not re.fullmatch(r"\d{2}-\d{2}-\d{2}", fecha_txt):
        raise ValueError("FECHA_FORMATO")

    try:
        fecha_obj = datetime.strptime(fecha_txt, "%d-%m-%y")
    except ValueError:
        raise ValueError("FECHA_INVALIDA")

    # Obligatorios no vacíos
    for key, val in {
        "CAPACITADOR", capacitador,
        "CADENA", cadena,
        "ZONA", zona,
        "DIRECCION", direccion,
        "CANTIDAD", cantidad,
        "VENDEDORES", vendedores_txt,
    }.items():
        if not val.strip():
            raise ValueError(f"VACIO_{key}")

    # Normalizar vendedores (acepta coma o punto y coma)
    vendedores = ", ".join(
        [x.strip() for x in re.split(r"[;,]", vendedores_txt) if x.strip()]
    )
    if not vendedores:
        raise ValueError("VACIO_VENDEDORES")

    return {
        "fecha": fecha_obj.strftime("%d-%m-%y"),   # normalizada
        "capacitador": capacitador.strip(),
        "cadena": cadena.strip(),
        "zona": zona.strip(),
        "direccion": direccion.strip(),
        "cantidad": cantidad.strip(),
        "vendedores": vendedores,
        "comentarios": comentarios.strip(),
    }

def enviar_a_forms(datos: dict):
    if not FORM_URL:
        logging.warning("FORM_URL no configurado, no se envia a Google Forms")
        return
    
    payload = {
        "entry.728470323": datos["fecha"],
        "entry.1492019641": datos["capacitador"],
        "entry.1011740523": datos["cadena"],
        "entry.959735072": datos["zona"],
        "entry.1569623492": datos["direccion"],
        "entry.1326869635": datos["cantidad"],
        "entry.1441118373": datos["vendedores"],
        "entry.1960523388": datos["comentarios"],
    }

    response = requests.post(FORM_URL, data=payload, timeout=10)
    response.raise_for_status()

# -------------------------------------------------
# HANDLER
# -------------------------------------------------
    
async def procesar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        datos = parsear_mensaje(update.message.text)
        logging.info("Registro validado: %s", datos)

        enviar_a_forms(datos)

        await update.message.reply_text(
            "✅ Registro cargado correctamente:\n"
            f"Fecha: {datos['fecha']}\n"
            f"Capacitador: {datos['capacitador']}\n"
            f"Cadena: {datos['cadena']}\n"
            f"Zona: {datos['zona']}\n"
            f"Dirección: {datos['direccion']}\n"
            f"Cantidad: {datos['cantidad']}\n"
            f"Vendedores: {datos['vendedores']}\n"
            f"Comentarios: {datos['comentarios'] or '-'}"
        )

    except ValueError as e:
        errores = {
            "FORMATO": "Debes enviar 6 o 7 líneas.",
            "FECHA_FORMATO": "La fecha debe ser DD-MM-YY.",
            "FECHA_INVALIDA": "La fecha no es válida.",
            "VACIO_CAPACITADOR": "Falta el nombre del capacitador.",
            "VACIO_CADENA": "Falta la cadena.",
            "VACIO_ZONA": "Falta la zona.",
            "VACIO_DIRECCION": "Falta la dirección.",
            "VACIO_CANTIDAD": "Falta la cantidad.",
            "VACIO_VENDEDORES": "Faltan vendedores.",
        }
        await update.message.reply_text(errores.get(str(e), "Error de validación."))
    except Exception:
        logging.exception("Error inesperado")
        await update.message.reply_text("❌ Error interno del bot.")


#------------------------------------------------
# Main: iniciar el bot
#------------------------------------------------

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_mensaje))
    logging.info("Bot iniciado correctamente")
    app.run_polling()

if __name__ == "__main__":
    main()
        