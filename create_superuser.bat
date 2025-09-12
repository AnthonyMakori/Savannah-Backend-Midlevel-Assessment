@echo off
call venv\Scripts\activate.bat
python manage.py createsuperuser
pause