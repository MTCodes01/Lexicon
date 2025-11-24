"""
Background tasks for Lexicon using Celery.
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.core.celery_app import celery_app
from api.database import SessionLocal
from api.core import crud
from api.core.email_service import EmailService
from api.modules.tasks.models import Task, TaskStatus
import asyncio


@celery_app.task(name="api.core.tasks.check_task_deadlines")
def check_task_deadlines():
    """
    Periodic task to check for upcoming and overdue task deadlines.
    Groups tasks by user and sends one email per user with all their pending tasks.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        
        # Time windows
        in_24h = now + timedelta(hours=24)
        in_1h = now + timedelta(hours=1)
        
        # Get all users
        users = crud.user_crud.get_multi(db, limit=10000)
        
        for user in users:
            # Get user's incomplete tasks with deadlines
            user_tasks = (
                db.query(Task)
                .filter(
                    Task.user_id == user.id,
                    Task.due_date.isnot(None),
                    Task.status.notin_([TaskStatus.COMPLETED, TaskStatus.CANCELLED]),
                )
                .all()
            )
            
            if not user_tasks:
                continue
            
            # Categorize tasks
            tasks_24h = []
            tasks_1h = []
            tasks_overdue = []
            
            for task in user_tasks:
                due_date = task.due_date
                
                # Skip if no due date
                if not due_date:
                    continue
                
                # Check if overdue
                if due_date < now:
                    # Only send overdue notification if not already sent
                    if not task.notification_overdue_sent:
                        tasks_overdue.append(task)
                        task.notification_overdue_sent = True
                        task.last_notification_at = now
                
                # Check if due in 1 hour
                elif due_date <= in_1h:
                    if not task.notification_1h_sent:
                        tasks_1h.append(task)
                        task.notification_1h_sent = True
                        task.last_notification_at = now
                
                # Check if due in 24 hours
                elif due_date <= in_24h:
                    if not task.notification_24h_sent:
                        tasks_24h.append(task)
                        task.notification_24h_sent = True
                        task.last_notification_at = now
            
            # Send grouped notification if there are any tasks
            if tasks_24h or tasks_1h or tasks_overdue:
                # Send email asynchronously
                asyncio.run(
                    EmailService.send_task_deadline_notifications(
                        user=user,
                        tasks_24h=tasks_24h,
                        tasks_1h=tasks_1h,
                        tasks_overdue=tasks_overdue,
                    )
                )
                
                # Commit notification tracking updates
                db.commit()
                
                print(f"✅ Sent deadline notification to {user.email}: "
                      f"{len(tasks_overdue)} overdue, {len(tasks_1h)} in 1h, {len(tasks_24h)} in 24h")
        
        return {
            "status": "success",
            "checked_at": now.isoformat(),
            "users_notified": sum(1 for u in users if any([tasks_24h, tasks_1h, tasks_overdue])),
        }
    
    except Exception as e:
        print(f"❌ Error checking task deadlines: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        db.close()


@celery_app.task(name="api.core.tasks.send_test_email")
def send_test_email(to_email: str):
    """Test task to verify Celery and email are working."""
    asyncio.run(
        EmailService.send_email(
            to_email=to_email,
            subject="Test Email from Lexicon",
            html_content="<h1>Celery is working!</h1><p>This is a test email.</p>",
            text_content="Celery is working! This is a test email.",
        )
    )
    return {"status": "sent", "to": to_email}
