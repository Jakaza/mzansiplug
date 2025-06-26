from django import template
register = template.Library()

@register.simple_tag
def querystring(request_get, key, value):
    dict_ = request_get.copy()
    dict_[key] = value
    return dict_.urlencode()
