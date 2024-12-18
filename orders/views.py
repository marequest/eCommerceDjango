import json
from datetime import datetime

from django.contrib import messages
from django.core.mail import EmailMessage

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from carts.models import CartItem
from orders.forms import OrderForm
from orders.models import Order, Payment, OrderProduct
from store.models import Product

import traceback
import logging
logger = logging.getLogger('django')


# Create your views here.
def place_order(request, quantity=0, total=0):
    current_user = request.user

    # If cart count is 0, redirect back to shop
    cart_items = CartItem.objects.filter(user=current_user)
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('store')

    grand_total = 0
    tax = 0
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.phone = form.cleaned_data['phone']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.country = form.cleaned_data['country']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()
            # Generate Order number
            d = datetime.today()
            current_date = d.strftime('%Y%m%d')
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()

            order = Order.objects.get(user=current_user, order_number=order_number, is_ordered=False)
            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    else:
        return redirect('checkout')


@csrf_exempt
def payments(request):
    body = json.loads(request.body)

    order = Order.objects.get(user=request.user, is_ordered=False, order_number=body['orderID'])

    payment = Payment(
        user=request.user,
        payment_id=body['transactionID'],
        payment_method=body['payment_method'],
        amount_paid=order.order_total,
        status=body['status'],
    )
    payment.save()

    order.payment = payment
    order.is_ordered = True
    order.save()

    # Move the cart items to Order Product Table
    cart_items = CartItem.objects.filter(user=request.user)

    for cart_item in cart_items:
        order_product = OrderProduct()
        order_product.user_id = request.user.id
        order_product.order_id = order.id
        order_product.product_id = cart_item.product_id
        order_product.quantity = cart_item.quantity
        order_product.product_price = cart_item.product.price
        order_product.payment = payment
        order_product.is_ordered = True
        # order_product.variation
        order_product.save()

        cart_item = CartItem.objects.get(id=cart_item.id)
        product_variations = cart_item.variations.all()
        order_product = OrderProduct.objects.get(id=order_product.id)
        order_product.variations.set(product_variations)
        order_product.save()

        # Reduce the qunatity of the sold products
        product = Product.objects.get(id=cart_item.product_id)
        if (product.stock - cart_item.quantity >= 0):
            product.stock -= cart_item.quantity
        else:
            return HttpResponse('Not enough in stock')
        product.save()

    # Clear cart
    CartItem.objects.filter(user=request.user).delete()

    # Send email to customer
    try:
        mail_subject = 'Thank you for shopping with us.'
        message = render_to_string('orders/order_received_email.html', {
            'user': request.user,
            'order': order,
        })
        to_email = request.user.email
        send_email = EmailMessage(mail_subject, message, to=[to_email])
        send_email.send()
    except Exception as e:
        logger.error("Error sending email: %s", str(e))
        logger.error(traceback.format_exc())  # Log full stack trace for debugging
        print(traceback.format_exc())


    messages.success(request, 'Thank you for shopping with us!')
    # Send order number and transaction id back to onApprove
    data = {
        'order_number': order.order_number,
        'transaction_id': payment.payment_id,
        # 'order_date': order.created_at,
        # 'status': order.status,
    }
    return JsonResponse(data)
    # return render(request, 'orders/payments.html')


@csrf_exempt
def order_complete(request):
    order_number = request.GET.get('order_number')
    payment_id = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number=order_number, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(payment_id=payment_id)

        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'payment_id': payment.payment_id,
            'payment': payment,
            'subtotal': subtotal,
        }
        return render(request, 'orders/order_complete.html', context)
    except(Payment.DoesNotExist, Order.DoesNotExist) as e:
        print("GRESKA")
        print(e)
        # return redirect('home')
        return render(request, 'orders/order_complete.html')

