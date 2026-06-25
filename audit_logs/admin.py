from django.contrib import admin
from audit_logs.models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'module', 'timestamp', 'ip_address')
    list_filter = ('action', 'module', 'timestamp')
    search_fields = ('user__email', 'action', 'module', 'details')
    readonly_fields = ('user', 'action', 'module', 'timestamp', 'ip_address', 'details')
