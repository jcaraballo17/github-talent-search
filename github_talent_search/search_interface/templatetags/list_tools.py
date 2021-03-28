from collections import Mapping, Counter
from typing import Dict

from django import template

register = template.Library()


@register.filter
def get_most_common_email(emails_occurrence: Dict) -> str:
    if not isinstance(emails_occurrence, Mapping):
        return ''
    try:
        return Counter(emails_occurrence).most_common(1)[0][0]
    except (TypeError, IndexError):
        return ''
