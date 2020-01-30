from django import template
 
register = template.Library()
 
@register.filter(name="multiply")
def multipliy(value, args):
    return value * args
    
@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg