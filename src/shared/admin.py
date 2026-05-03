from axes.admin import (
    AccessAttemptAdmin as BaseAccessAttemptAdmin,
)
from axes.admin import (
    AccessFailureLogAdmin as BaseAccessFailureLogAdmin,
)
from axes.admin import (
    AccessLogAdmin as BaseAccessLogAdmin,
)
from axes.models import AccessAttempt, AccessFailureLog, AccessLog
from django.contrib import admin
from unfold.admin import ModelAdmin

admin.site.unregister(AccessAttempt)
admin.site.unregister(AccessLog)
admin.site.unregister(AccessFailureLog)


@admin.register(AccessAttempt)
class AccessAttemptAdmin(BaseAccessAttemptAdmin, ModelAdmin):
    pass


@admin.register(AccessLog)
class AccessLogAdmin(BaseAccessLogAdmin, ModelAdmin):
    pass


@admin.register(AccessFailureLog)
class AccessFailureLogAdmin(BaseAccessFailureLogAdmin, ModelAdmin):
    pass
