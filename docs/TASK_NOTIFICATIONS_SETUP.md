# Task Deadline Email Notifications - Setup Guide

## 🎯 Overview

Automated email notifications for task deadlines using Celery background workers.

---

## ✅ What's Implemented

**Notification Types:**
- 📅 **24-hour warning:** "Your task is due tomorrow"
- ⏰ **1-hour warning:** "Your task is due in 1 hour"
- 🚨 **Overdue alert:** "Your task is overdue"

**Smart Features:**
- ✅ Groups multiple tasks into ONE email per user
- ✅ Sorts tasks by priority (urgent → high → medium → low)
- ✅ Only sends for incomplete tasks (skips completed/cancelled)
- ✅ Tracks notifications to prevent duplicates
- ✅ Beautiful HTML email template with priority colors

---

## 📋 Setup Instructions

### 1. Gmail App Password

To use Gmail for sending emails, you need an **App Password** (not your regular Gmail password):

1. Go to your Google Account: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Scroll down to **App passwords**
4. Click **Select app** → Choose "Mail"
5. Click **Select device** → Choose "Other" → Type "Lexicon"
6. Click **Generate**
7. Copy the 16-character password (no spaces)

### 2. Update Environment Variables

Edit `.env` file in the project root:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com           # Your Gmail address
SMTP_PASSWORD=xxxx xxxx xxxx xxxx        # The app password from step 1
SMTP_FROM_EMAIL=your-email@gmail.com     # Same as SMTP_USER
SMTP_USE_TLS=true
APP_URL=http://localhost:3000            # Your frontend URL
```

### 3. Update Database Schema

The Task model now has notification tracking fields. Update your database:

```powershell
# Option A: Restart API (auto-creates new columns)
# Stop and restart the API server

# Option B: Manual SQL (if needed)
docker-compose exec postgres psql -U lexicon -d lexicon_db -c "
ALTER TABLE tasks 
ADD COLUMN IF NOT EXISTS notification_24h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS notification_1h_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS notification_overdue_sent BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS last_notification_at TIMESTAMP;
"
```

### 4. Start Celery Worker

Open a **new terminal** and run:

```powershell
cd d:\Github\Lexicon
api\.venv\Scripts\activate
celery -A api.core.celery_app worker --loglevel=info --pool=solo
```

Or use the batch file:
```powershell
.\start_celery_worker.bat
```

### 5. Start Celery Beat (Scheduler)

Open **another new terminal** and run:

```powershell
cd d:\Github\Lexicon
api\.venv\Scripts\activate
celery -A api.core.celery_app beat --loglevel=info
```

Or use the batch file:
```powershell
.\start_celery_beat.bat
```

---

## 🧪 Testing

### Test Email Sending

```python
# In Python shell
from api.core.celery_app import celery_app
from api.core.tasks import send_test_email

# Send test email
result = send_test_email.delay("your-email@gmail.com")
print(result.get())  # Should print: {'status': 'sent', 'to': 'your-email@gmail.com'}
```

### Test Deadline Checking

```python
# Create a test task with a deadline in 23 hours
from api.database import SessionLocal
from api.modules.tasks.models import Task
from datetime import datetime, timedelta

db = SessionLocal()
user = db.query(User).first()

test_task = Task(
    user_id=user.id,
    title="Test Deadline Task",
    description="This should trigger a 24h notification",
    priority="high",
    status="todo",
    due_date=datetime.utcnow() + timedelta(hours=23),
)
db.add(test_task)
db.commit()

# Manually trigger the deadline check
from api.core.tasks import check_task_deadlines
result = check_task_deadlines.delay()
print(result.get())
```

---

## 🔄 How It Works

1. **Celery Beat** runs every hour and triggers `check_task_deadlines` task
2. **Worker** processes the task:
   - Fetches all users
   - For each user, finds incomplete tasks with deadlines
   - Groups tasks into 3 categories: 24h, 1h, overdue
   - Sends ONE email per user with all their tasks
   - Marks notifications as sent to prevent duplicates
3. **Email** is sent via Gmail SMTP with beautiful HTML template

---

## 📊 Monitoring

### Check Celery Worker Status

```powershell
# View active tasks
celery -A api.core.celery_app inspect active

# View scheduled tasks
celery -A api.core.celery_app inspect scheduled

# View worker stats
celery -A api.core.celery_app inspect stats
```

### Check Notification History

```sql
-- See which tasks have notifications sent
SELECT 
    title, 
    due_date,
    notification_24h_sent,
    notification_1h_sent,
    notification_overdue_sent,
    last_notification_at
FROM tasks
WHERE due_date IS NOT NULL
ORDER BY due_date;
```

---

## 🐛 Troubleshooting

### Email Not Sending

1. **Check Gmail App Password:**
   - Make sure you're using an App Password, not your regular password
   - Verify 2-Step Verification is enabled

2. **Check SMTP Settings:**
   ```python
   from api.config import settings
   print(f"SMTP_HOST: {settings.SMTP_HOST}")
   print(f"SMTP_USER: {settings.SMTP_USER}")
   print(f"SMTP_PASSWORD: {'***' if settings.SMTP_PASSWORD else 'NOT SET'}")
   ```

3. **Check Celery Logs:**
   - Look for errors in the Celery worker terminal
   - Check for "Failed to send email" messages

### Worker Not Running

```powershell
# Check if Redis is running
docker-compose ps redis

# Restart Redis if needed
docker-compose restart redis

# Check Celery can connect to Redis
celery -A api.core.celery_app inspect ping
```

### Notifications Not Triggering

1. **Verify task has due_date set**
2. **Check task status is not completed/cancelled**
3. **Verify notification flags:**
   ```sql
   SELECT * FROM tasks WHERE id = 'your-task-id';
   ```
4. **Manually trigger check:**
   ```python
   from api.core.tasks import check_task_deadlines
   check_task_deadlines.delay()
   ```

---

## 🚀 Production Deployment

For production, use a process manager:

### Option 1: Supervisor (Linux)

```ini
[program:lexicon-celery-worker]
command=/path/to/venv/bin/celery -A api.core.celery_app worker --loglevel=info
directory=/path/to/lexicon
user=www-data
autostart=true
autorestart=true

[program:lexicon-celery-beat]
command=/path/to/venv/bin/celery -A api.core.celery_app beat --loglevel=info
directory=/path/to/lexicon
user=www-data
autostart=true
autorestart=true
```

### Option 2: Docker Compose

Add to `docker-compose.yml`:

```yaml
  celery-worker:
    build:
      context: ./api
    command: celery -A api.core.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql://lexicon:lexicon@postgres:5432/lexicon_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/1

  celery-beat:
    build:
      context: ./api
    command: celery -A api.core.celery_app beat --loglevel=info
    depends_on:
      - redis
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/1
```

---

## 🎨 Customization

### Change Notification Times

Edit `api/core/celery_app.py`:

```python
celery_app.conf.beat_schedule = {
    "check-task-deadlines": {
        "task": "api.core.tasks.check_task_deadlines",
        "schedule": 1800.0,  # Run every 30 minutes instead of 1 hour
    },
}
```

### Customize Email Template

Edit `api/templates/task_deadlines.html` to change:
- Colors and styling
- Layout and structure
- Content and wording

### Add More Notification Types

Edit `api/core/tasks.py` to add:
- 3-day warning
- Weekly digest
- Custom reminder times per task

---

## 📝 Summary

**Running Services:**
1. PostgreSQL (Docker)
2. Redis (Docker)
3. FastAPI Backend
4. Next.js Frontend
5. **Celery Worker** ← NEW
6. **Celery Beat** ← NEW

**Total: 6 services running**

All set! Your task deadline notifications are now active! 🎉
