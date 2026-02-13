import discord
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from dotenv import load_dotenv
import os

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

creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEYFILE, scope)
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
        "DíaSemana"
    ])

# ==============================
# DISCORD
# ==============================

intents = discord.Intents.default()
intents.voice_states = True
intents.members = True

client = discord.Client(intents=intents)

sessions = {}

@client.event
async def on_ready():
    print(f"Bot conectado como {client.user}")
    print(f"Trackeando USER_ID = {TRACK_USER_ID}")

@client.event
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
            ]

            sheet.append_row(row)
            print(f"Sesión de {channel} guardada")

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
            ]

            sheet.append_row(row)

        sessions[member.id] = (member.name, after.channel.name, now)
        print(f"Cambio a canal {after.channel.name} registrado")

client.run(TOKEN)