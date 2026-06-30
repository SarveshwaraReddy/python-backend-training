import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def notify_hr(self, action_type, details):
    """
    Sends a system notification to the HR team via email/logs when an event occurs.
    """
    logger.info(f"HR Notification triggered: {action_type} - {details}")
    try:
        subject = f"[HRMS ALERT] {action_type}"
        message = (
            f"Hello HR Team,\n\n"
            f"An event has been logged on the HRMS Platform:\n\n"
            f"Event Type: {action_type}\n"
            f"Details: {details}\n\n"
            f"Task ID: {self.request.id}\n\n"
            f"Best regards,\nHRMS Automation System"
        )
        
        if action_type == "FAIL_TEST":
            raise ConnectionError("Notification service timeout.")
            
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'system@company.local',
            ['hr@company.local'],
            fail_silently=False,
        )
        logger.info("HR Notification successfully sent to hr@company.local")
        return f"HR Notification sent for {action_type}"
    except Exception as e:
        logger.warning(f"Error sending HR Notification. Retrying in 30 seconds... (Attempt {self.request.retries + 1}/5). Error: {e}")
        raise self.retry(exc=e)
