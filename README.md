# TimeTrackerBot
Bot de Discord que registra el tiempo de un usuario en canales de voz y guarda cada sesion en una hoja de Google Sheets. El bot monitorea entradas, salidas y cambios de canal, y escribe: usuario, canal, hora de entrada/salida, duracion y fecha.

## Requisitos
- Python 3.10+ (recomendado)
- Cuenta de servicio de Google con acceso a la hoja
- Bot de Discord con permisos para leer estados de voz

## Dependencias
Instaladas desde [requirements.txt](requirements.txt):
- discord.py
- gspread
- oauth2client
- python-dotenv
- pyinstaller (solo si queres generar el .exe)

## Configuracion
Crear un archivo `.env` en la raiz del proyecto con estas variables:

```env
DISCORD_TRACK_USER_ID=123456789012345678
DISCORD_BOT_TOKEN=TU_TOKEN
GOOGLE_SERVICE_ACCOUNT_FILE=./ruta/al/service_account.json
GOOGLE_SHEET_NAME=NombreDeLaHoja
```

Notas:
- `DISCORD_TRACK_USER_ID` es el ID del usuario a trackear (solo ese usuario se registra).
- Para obtener el ID: Ajustes de usuario -> Avanzado -> activar Modo desarrollador. Luego clic izquierdo sobre el usuario -> Copiar ID de Usuario.
- `GOOGLE_SERVICE_ACCOUNT_FILE` debe apuntar al JSON de la cuenta de servicio.
- Comparti la hoja con el email de la cuenta de servicio.

## Instalacion
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecucion
Opcion 1 (recomendado en Windows):
```bat
run_bot.bat
```
`run_bot.bat` activa el venv y reinicia el bot si se cae.

Opcion 2 (manual):
```bash
python bot.py
```

## Build opcional (.exe)
Si queres generar un ejecutable con PyInstaller:
```bash
pyinstaller TimeTrackerBot.spec
```
El ejecutable queda en `dist\TimeTrackerBot\TimeTrackerBot.exe`.
