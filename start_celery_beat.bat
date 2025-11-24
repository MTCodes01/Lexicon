@echo off
REM Celery Beat Start Script
REM Run this to start the Celery beat scheduler for periodic tasks

cd /d %~dp0
call api\.venv\Scripts\activate
celery -A api.core.celery_app beat --loglevel=info
