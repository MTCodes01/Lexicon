@echo off
REM Celery Worker Start Script
REM Run this to start the Celery worker for background tasks

cd /d %~dp0
call api\.venv\Scripts\activate
celery -A api.core.celery_app worker --loglevel=info --pool=solo
