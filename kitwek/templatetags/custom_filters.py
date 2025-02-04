from django import template
from django.utils import timezone

register = template.Library()

@register.filter
def timesince_custom(value):
    now = timezone.now()  # Use timezone-aware datetime
    delta = now - value
    
    seconds = delta.total_seconds()
    
    if seconds < 60:
        return f"{int(seconds)} sec{'s' if seconds != 1 else ''} ago"
    elif seconds < 3600:  # Less than an hour
        minutes = seconds // 60
        return f"{int(minutes)} min{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:  # Less than a day
        hours = seconds // 3600
        return f"{int(hours)} hr{'s' if hours != 1 else ''} ago"
    elif seconds < 604800:  # Less than a week
        days = seconds // 86400
        return f"{int(days)} day{'s' if days != 1 else ''} ago"
    elif seconds < 2419200:  # Less than a month (30 days)
        weeks = seconds // 604800
        return f"{int(weeks)} wk{'s' if weeks != 1 else ''} ago"
    elif seconds < 31536000:  # Less than a year
        months = seconds // 2592000
        return f"{int(months)} mo{'s' if months != 1 else ''} ago"
    else:  # One year or more
        years = seconds // 31536000
        return f"{int(years)} yr{'s' if years != 1 else ''} ago"





# email *******
@register.filter
def hide_email(value):
    """Replaces the last 3 characters of the local part with **** and hides the domain name."""
    if value and "@" in value:
        local_part, domain_part = value.split("@", 1)

        # Replace the last 3 characters of the local part with "****"
        local_part_hidden = local_part[:-3] + "****" if len(local_part) > 3 else "****"

        # Split the domain part and replace the domain name (between @ and .) with "****"
        domain_name, domain_extension = domain_part.split(".", 1)
        domain_hidden = f"****.{domain_extension}"

        return f"{local_part_hidden}@{domain_hidden}"
    return value