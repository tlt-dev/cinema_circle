from django import template
register = template.Library()


@register.filter
def mongo_id(value):
    return str(value['_id'])
