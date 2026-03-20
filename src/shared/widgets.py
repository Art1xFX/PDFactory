from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING

from django.template.loader import get_template

if TYPE_CHECKING:
    from django.utils.functional import _StrOrPromise as StrOrPromise
    from django.utils.safestring import SafeString


class Target(Enum):
    SELF = "_self"
    BLANK = "_blank"
    PARENT = "_parent"
    TOP = "_top"


def a(text: StrOrPromise | SafeString, *, href: str, target: Target, **kwargs) -> SafeString:
    template = get_template("shared/widgets/a.html")

    return template.render(
        {
            "text": text,
            "attrs": {
                "href": href,
                "target": target.value,
                **kwargs,
            },
        }
    )
