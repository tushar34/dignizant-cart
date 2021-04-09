from django.contrib import admin
from django.urls import path,include
from . import views
from .views import *
from django.contrib.auth.decorators import login_required
app_name = 'ap1'
urlpatterns = [
     path('', views.home, name='home'),
     #path('accounts/profile', views.home, ''),
     path('checkout/', login_required(Checkoutview.as_view()), name='checkout'),
     path('product/<slug>/', ItemDetailView.as_view(),name='product'),
     path('add-to-card/<slug>/', add_to_cart, name='add-to-card'),
     path('add-coupon/', login_required(add_coupon.as_view()), name='add-coupon'),
     path('remove-to-card/<slug>/', remove_from_cart, name='remove-from-card'),
     path('OrderSummaryView/', login_required(OrderSummaryView.as_view()), name='OrderSummaryView'),
     path('remove-single-item-from-card/<slug>/', remove_single_item_from_cart, name='remove-single-item-from-card'),
     path('payment-view/<payment_option>/', login_required(PaymentView.as_view()), name='payment-view'),
     path('request-refund/', login_required(RequestRefundView.as_view()), name='request-refund'),

]
