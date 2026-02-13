@echo off
title TimeTrackerBot
cd /d %~dp0
call venv\Scripts\activate

:loop
python bot.py
timeout /t 5 >nul
goto loop
