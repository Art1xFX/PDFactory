from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from guardian.admin import GuardedModelAdmin
from guardian.shortcuts import get_objects_for_user
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import (
    ModelAdmin,
)
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

User = get_user_model()


admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, GuardedModelAdmin, ModelAdmin, SimpleHistoryAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm

    def get_queryset(self, request):
        queryset = super().get_queryset(request)

        if not request.user.is_superuser:
            queryset = queryset.exclude(pk=User.get_anonymous().pk)

        return get_objects_for_user(
            request.user,
            [
                "user.view_user_personal_data",
                "user.view_user",
                "user.change_user_personal_data",
                "user.change_user",
                "user.delete_user",
            ],
            queryset,
            any_perm=True,
            accept_global_perms=True,
        ).distinct()

    def has_view_permission(self, request, obj=None):
        perms = ["user.view_user_personal_data", "user.view_user"]

        if obj is not None:
            return any(request.user.has_perm(perm, obj) for perm in perms)

        return (
            super().has_view_permission(request, obj)
            or get_objects_for_user(
                request.user,
                perms,
                self.model.objects.all(),
                any_perm=True,
                accept_global_perms=False,
            ).exists()
        )

    def has_change_permission(self, request, obj=None):
        perms = ["user.change_user_personal_data", "user.change_user"]

        if obj is not None:
            return any(request.user.has_perm(perm, obj) for perm in perms)

        return (
            super().has_change_permission(request, obj)
            or get_objects_for_user(
                request.user,
                perms,
                self.model.objects.all(),
                any_perm=True,
                accept_global_perms=False,
            ).exists()
        )

    def has_delete_permission(self, request, obj=None):
        if obj is not None:
            return request.user.has_perm("user.delete_user", obj)

        return (
            super().has_delete_permission(request, obj)
            or get_objects_for_user(
                request.user,
                ["user.delete_user"],
                self.model.objects.all(),
                any_perm=True,
                accept_global_perms=False,
            ).exists()
        )

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        perms = ["user.view_user", "user.change_user"]

        if not any(request.user.has_perm(perm, obj) for perm in perms):
            fieldsets = [
                fieldset
                for fieldset in fieldsets
                if fieldset[0]
                in (
                    None,
                    _("Personal info"),
                    _("Important dates"),
                )
            ]

        return fieldsets

    def get_readonly_fields(self, request, obj=...):
        readonly_fields = super().get_readonly_fields(request, obj)

        if not request.user.has_perm("user.change_user", obj):
            readonly_fields += ("username", "last_login", "date_joined")

        return readonly_fields


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin, SimpleHistoryAdmin):
    pass
