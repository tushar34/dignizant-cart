from django.contrib import messages
from django.shortcuts import render,get_object_or_404,redirect
from django.utils import timezone
from urllib3 import HTTPResponse

from .forms import Checkoutform,CouponForm,RefundForm
from .models import *
from django.views.generic import DetailView,View
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from django.shortcuts import reverse
import stripe
from django.conf import settings
import random
import string

#stripe.api_key = 'sk_test_51Ibk4KSGafLm2PSq913WdziBK9Xiag7aADHkoiOjSUUblysgCH1e6q4fr76e09u4rRpogYRjJZezjn7xCmUgTEOs00wcgcrNRb'

stripe.api_key = settings.STRIPE_SECRET_KEY
def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request,"home.html",context)

def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits,k=20))


class Checkoutview(View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = Checkoutform()
            context = {
                'form': form,
                'couponform' : CouponForm(),
                'order': order,
            'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout.html", context)
        except ObjectDoesNotExist:
            messages.success(self.request, "you do not have an active order")
            return redirect("ap1:cheakout")

    def post(self, *args, **kwargs):
        form = Checkoutform(self.request.POST or None)
        try:
            print(form.is_valid())
            order = Order.objects.get(user=self.request.user,ordered=False)
            if form.is_valid():
                print('hello')
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = Billingaddress(
                    user=self.request.user,
                    street_address=street_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip,
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                return redirect('ap1:payment-view', payment_option='stripe')
            messages.warning(self.request,"failed to checkout")
            return redirect('ap1:PaymentView')
        except ObjectDoesNotExist:
            messages.warning(self.request, "you do not have an active order")
            return redirect('ap1:checkout')

def product(request):
    return render(request, "products.html")

class ItemDetailView(DetailView):
    model = Item
    template_name = "products.html"


class OrderSummaryView(View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user,ordered=False)
            context = {
                'object': order
            }
            return render(self.request,'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("ap1:home")

def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = Orderitem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("ap1:OrderSummaryView", )
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("ap1:OrderSummaryView", )
    else:
        order_date = timezone.now()
        order = Order.objects.create(
            user=request.user, order_date=order_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("ap1:product", slug=slug)

def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = Orderitem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]

            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect("ap1:OrderSummaryView")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("ap1:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("ap1:product", slug=slug)

def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = Orderitem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)

            messages.info(request, "Quantity was  updated.")
            return redirect("ap1:OrderSummaryView")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("ap1:product")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("ap1:product")



class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order': order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, "payment.html", context)
        else:
            messages.warning(self.request,'you have no billing address')
            return redirect("ap1:checkout")
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total()*100)

        try:
            charge = stripe.Charge.create(
                amount=amount,  # cents
                currency="INR",
                source=token
            )

            # create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_item = order.items.all()
            order_item.update(ordered=True)
            for item in order_item:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            messages.success(self.request, "Your order was successful!")
            return redirect("/")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect("/")

        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect("/")

        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")

            return redirect("/")

        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Not authenticated")
            return redirect("/")

        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect("/")

        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(
                self.request, "Something went wrong. You were not charged. Please try again.")
            return redirect("/")

        except Exception as e:
            # send an email to ourselves
            messages.error(
                self.request, "A serious error occurred. We have been notifed.")
            return redirect("/")

def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon
    except ObjectDoesNotExist:
        messages.success(request, "this coupon does not exist")
        return redirect("ap1:cheakout")
class  add_coupon(View):
    def post(self,*args,**kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user=self.request.user,ordered=False)
                order.coupon = get_coupon(self.request,code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("ap1:checkout")
            except ObjectDoesNotExist:
                messages.info(self.request, "you do not have an active order")
                return redirect("ap1:checkout")

class RequestRefundView(View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_request = True
                order.save()

                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "Your request was received.")
                return redirect("ap1:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not exist.")
                return redirect("ap1:request-refund")