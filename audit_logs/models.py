from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    action = models.CharField(max_length=50) # LOGIN, LOGOUT, CREATE, UPDATE, DELETE
    module = models.CharField(max_length=100) # Employees, Departments, Accounts, Auth
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.email if self.user else "Anonymous"
        return f"{user_str} - {self.action} on {self.module} at {self.timestamp}"
