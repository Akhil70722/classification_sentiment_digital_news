@echo off
cd /d "%~dp0"
.venv\Scripts\activate
python manage.py runserver
pause

