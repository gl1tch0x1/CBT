from django import template

register = template.Library()


@register.filter
def lookup(dictionary, key):
    """Template filter to lookup dictionary values by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(str(key))
    return None


@register.filter
def subtract(value, arg):
    """Template filter to subtract two numbers"""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0


@register.filter
def multiply(value, arg):
    """Template filter to multiply two numbers"""
    try:
        return int(value) * int(arg)
    except (ValueError, TypeError):
        return 0
