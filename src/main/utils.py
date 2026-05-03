from dynaconf.utils.parse_conf import Lazy


def _format_translation(value, **context):  # pylint: disable=unused-argument
    from django.utils.translation import gettext_lazy as _  # pylint: disable=import-outside-toplevel

    return _(value)


def _format_link(value, **context):  # pylint: disable=unused-argument
    from django.urls import reverse_lazy as reverse  # pylint: disable=import-outside-toplevel

    return reverse(**value)


def gettext_lazy(value):
    """
    Wrapper around Django's gettext_lazy to be used in Dynaconf settings.

    See: https://github.com/dynaconf/dynaconf/issues/648
    """
    return Lazy(value, formatter=_format_translation)


def reverse_lazy(viewname, query=None):
    """
    Wrapper around Django's reverse_lazy to be used in Dynaconf settings.

    See: https://github.com/dynaconf/dynaconf/issues/648
    """
    return Lazy(
        {
            "viewname": viewname,
            "query": query,
        },
        formatter=_format_link,
    )


def has_view_user_permission(request):
    from guardian.shortcuts import get_objects_for_user  # pylint: disable=import-outside-toplevel

    return get_objects_for_user(
        request.user,
        ["user.view_user_personal_data", "user.view_user"],
        any_perm=True,
        accept_global_perms=True,
    ).exists()
