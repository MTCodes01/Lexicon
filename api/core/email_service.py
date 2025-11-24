"""
Email service for sending notifications.
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from typing import List
from api.config import settings
from api.core.models import User
from api.modules.tasks.models import Task

# Setup Jinja2 for email templates
template_dir = Path(__file__).parent.parent / "templates"
template_dir.mkdir(exist_ok=True)

jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


class EmailService:
    """Service for sending emails."""

    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
    ) -> bool:
        """Send an email via SMTP."""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = settings.SMTP_FROM_EMAIL
            message["To"] = to_email
            message["Subject"] = subject

            # Attach both plain text and HTML versions
            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            message.attach(part1)
            message.attach(part2)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                use_tls=settings.SMTP_USE_TLS,
            )
            return True
        except Exception as e:
            print(f"Failed to send email to {to_email}: {e}")
            return False

    @staticmethod
    async def send_task_deadline_notifications(
        user: User,
        tasks_24h: List[Task],
        tasks_1h: List[Task],
        tasks_overdue: List[Task],
    ) -> bool:
        """
        Send grouped task deadline notifications to a user.
        Groups all pending tasks into one email organized by urgency and priority.
        """
        # Skip if no tasks to notify about
        if not (tasks_24h or tasks_1h or tasks_overdue):
            return False

        # Sort tasks by priority (urgent > high > medium > low)
        priority_order = {"urgent": 0, "high": 1, "medium": 2, "low": 3}

        def sort_by_priority(tasks):
            return sorted(tasks, key=lambda t: priority_order.get(t.priority, 4))

        tasks_24h = sort_by_priority(tasks_24h)
        tasks_1h = sort_by_priority(tasks_1h)
        tasks_overdue = sort_by_priority(tasks_overdue)

        # Render email template
        try:
            template = jinja_env.get_template("task_deadlines.html")
            html_content = template.render(
                user=user,
                tasks_24h=tasks_24h,
                tasks_1h=tasks_1h,
                tasks_overdue=tasks_overdue,
                app_url=settings.APP_URL or "http://localhost:3000",
            )

            # Plain text version
            text_content = f"""
Hi {user.full_name or user.username},

You have tasks that need your attention:
"""
            if tasks_overdue:
                text_content += f"\n🚨 OVERDUE ({len(tasks_overdue)} tasks):\n"
                for task in tasks_overdue:
                    text_content += f"  - [{task.priority.upper()}] {task.title}\n"

            if tasks_1h:
                text_content += f"\n⏰ DUE IN 1 HOUR ({len(tasks_1h)} tasks):\n"
                for task in tasks_1h:
                    text_content += f"  - [{task.priority.upper()}] {task.title}\n"

            if tasks_24h:
                text_content += f"\n📅 DUE IN 24 HOURS ({len(tasks_24h)} tasks):\n"
                for task in tasks_24h:
                    text_content += f"  - [{task.priority.upper()}] {task.title}\n"

            text_content += f"\nView all tasks: {settings.APP_URL or 'http://localhost:3000'}/dashboard/tasks\n"

            # Determine subject based on urgency
            if tasks_overdue:
                subject = f"🚨 {len(tasks_overdue)} Overdue Task{'s' if len(tasks_overdue) > 1 else ''}"
            elif tasks_1h:
                subject = f"⏰ {len(tasks_1h)} Task{'s' if len(tasks_1h) > 1 else ''} Due in 1 Hour"
            else:
                subject = f"📅 {len(tasks_24h)} Task{'s' if len(tasks_24h) > 1 else ''} Due Tomorrow"

            # Send email
            return await EmailService.send_email(
                to_email=user.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )
        except Exception as e:
            print(f"Failed to render/send email template: {e}")
            return False
