import base64
import json
import discord
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os
from discord.ext import commands 
import webbrowser

# ==============================
# CONFIG (CADA PERSONA CAMBIA)
# ==============================

load_dotenv()

TRACK_USER_ID = int(os.getenv("DISCORD_TRACK_USER_ID")) # DISCORD USER ID
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
JSON_KEYFILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE")
SHEET_NAME = os.getenv("GOOGLE_SHEET_NAME")

# ==============================
# GOOGLE SHEETS
# ==============================

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

google_base64 = os.getenv("GOOGLE_SERVICE_ACCOUNT_BASE64")

if not google_base64:
    raise ValueError("Missing GOOGLE_SERVICE_ACCOUNT_BASE64")

# Decode base64
google_json = base64.b64decode(google_base64).decode("utf-8")

creds_dict = json.loads(google_json)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

gs_client = gspread.authorize(creds)

spreadsheet = gs_client.open(SHEET_NAME)
sheet = spreadsheet.sheet1

# Crear encabezados si no existen
if sheet.row_count == 0 or sheet.get_all_values() == []:
    sheet.append_row([
        "Usuario",
        "Canal",
        "Entrada",
        "Salida",
        "Duración (hh:mm:ss)",
        "Fecha",
        "DíaSemana",
        "Tarea"
    ])

# ==============================
# DISCORD
# ==============================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


sessions = {}
task = None
open_sheet_on_register = False

@bot.event
async def on_ready():
    # Inicializar la Task en vacio
    global task, open_sheet_on_register
    task = None
    open_sheet_on_register = False

    print(f"Bot conectado como {bot.user}")
    print(f"Trackeando USER_ID = {TRACK_USER_ID}")
    
    # Detectar si ya estaba en el voice
    bot.loop.create_task(start_tracking_if_already_in_voice())

# ==========================
# YA ESTABA EN EL VOICE
# ==========================
async def start_tracking_if_already_in_voice():
    await bot.wait_until_ready()

    for guild in bot.guilds:
        member = guild.get_member(TRACK_USER_ID)
        if member and member.voice and member.voice.channel:
            now = datetime.now()
            sessions[member.id] = (member.name, member.voice.channel.name, now)
            print(f"Usuario ya estaba en voice ({member.voice.channel.name}) -> tracking iniciado")
            return

@bot.event
async def on_voice_state_update(member, before, after):

    # Ignorar todos menos el usuario configurado
    if member.id != TRACK_USER_ID:
        return

    now = datetime.now()

    # ==========================
    # ENTRÓ A VOICE
    # ==========================
    if before.channel is None and after.channel is not None:
        sessions[member.id] = (member.name, after.channel.name, now)
        print(f"Entro a voice {after.channel.name}")

    # ==========================
    # SALIÓ DE VOICE
    # ==========================
    elif before.channel is not None and after.channel is None:
        if member.id in sessions:
            name, channel, start = sessions.pop(member.id)

            seconds = int((now - start).total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            duration = f"{hours:02d}:{minutes:02d}:{secs:02d}"

            row = [
                name,
                channel,
                start.strftime("%Y-%m-%d %H:%M:%S"),
                now.strftime("%Y-%m-%d %H:%M:%S"),
                duration,
                now.strftime("%Y-%m-%d"),
                now.strftime("%A"),
                task
            ]

            sheet.append_row(row)
            print(f"Sesión de {channel} guardada")
            if open_sheet_on_register:
                webbrowser.open(spreadsheet.url)

    # ==========================
    # CAMBIO DE CANAL
    # ==========================
    elif before.channel != after.channel:
        if member.id in sessions:
            name, channel, start = sessions.pop(member.id)

            seconds = int((now - start).total_seconds())
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            duration = f"{hours:02d}:{minutes:02d}:{secs:02d}"

            row = [
                name,
                channel,
                start.strftime("%Y-%m-%d %H:%M:%S"),
                now.strftime("%Y-%m-%d %H:%M:%S"),
                duration,
                now.strftime("%Y-%m-%d"),
                now.strftime("%A"),
                task
            ]

            sheet.append_row(row)
            if open_sheet_on_register:
                webbrowser.open(spreadsheet.url)

        sessions[member.id] = (member.name, after.channel.name, now)
        print(f"Cambio a canal {after.channel.name} registrado")

@bot.command()
async def setTask(ctx, task_id):
    global task
    try:
        if int(task_id) < 0:
            await ctx.send("El id de la tarea debe ser mayor a cero.")
        else:
            task = int(task_id)
            await ctx.send("Task seteada")
    except:
        await ctx.send("El id de la tarea debe ser un número.")


@bot.command()
async def getTask(ctx):
    global task
    await ctx.send(f"Current Task: {task}")

@bot.command()
async def cleanTask(ctx):
    global task
    task = None
    await ctx.send(f"Se limpió la tarea asignada.")

@bot.command()
async def openSheetOn(ctx):
    global open_sheet_on_register
    open_sheet_on_register = True
    await ctx.send("Auto-open Google Sheets ACTIVADO.")

@bot.command()
async def openSheetOff(ctx):
    global open_sheet_on_register
    open_sheet_on_register = False
    await ctx.send("Auto-open Google Sheets DESACTIVADO.")

@bot.command()
async def openSheetStatus(ctx):
    await ctx.send(f"Auto-open Sheets: {open_sheet_on_register}")


@bot.command(name="listCommands")
async def list_commands(ctx):
    help_text = """
** Lista de comandos disponibles**

`!setTask <id>`  
→ Asigna el ID de tarea actual (debe ser número mayor a 0).

`!getTask`  
→ Muestra la tarea actualmente seteada.

`!cleanTask`  
→ Limpia la tarea actual (queda en None).

`!openSheetOn`  
→ Activa la apertura automática de Google Sheets cuando se registra una sesión.

`!openSheetOff`  
→ Desactiva la apertura automática de Google Sheets.

`!openSheetStatus`  
→ Muestra si el auto-open de Sheets está activado o no.

`!helpme`  
→ Muestra esta ayuda.
"""
    await ctx.send(help_text)


bot.run(TOKEN)