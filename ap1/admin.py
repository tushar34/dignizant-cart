from django.contrib import admin
from.models import *

# Register your models here.


def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_request=False,refund_granted=True)

make_refund_accepted.short_description= 'Update orders to refund granted'

class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'ordered',
        'being_delivered',
        'received',
        'refund_request',
        'refund_granted',
        'billing_address',
        'payment',
        'coupon',
        ]
    list_display_links = [
        'billing_address',
        'payment',
        'coupon',
        'user',

    ]

    search_fields = [
        'user__username',
        'ref_code',

    ]
    list_filter = [
        'being_delivered',
        'received',
        'refund_request',
        'refund_granted',

    ]
    actions = [make_refund_accepted]


admin.site.register(Item)
admin.site.register(Order, OrderAdmin)
admin.site.register(Orderitem)
admin.site.register(Billingaddress)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)


