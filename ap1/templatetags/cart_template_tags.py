from django import template
from ap1.models import Order

register = template.Library()

@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qa = Order.objects.filter(user=user, ordered=False)
        if qa.exists():
            return qa[0].items.count()
    return 0
