import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

import json
from .models import *


def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
    except:
        cart = {}

    items = []
    order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    for i in cart:
        try:
            cartItems += cart[i]['quantity']

            product = Product.objects.get(id=i)
            total = (product.price * cart[i]['quantity'])

            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': cart[i]['quantity'],
                'get_total': total
            }

            items.append(item)
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}


def product_sales_pipeline(product_name, product_price):
    stripe_product_obj = stripe.Product.create(name=product_name) #create product in stripe
    stripe_product_id = stripe_product_obj.id #id of stripe product created
    stripe_price_obj = stripe.Price.create(
        product = stripe_product_id,
        unit_amount = product_price,
        currency = 'inr'
    )
    base_endpoint = 'https://micro-ecom-web.onrender.com'
    success_url = f"{base_endpoint}/"
    cancel_url = f"{base_endpoint}/payments/cancelled/"

    checkout_session = stripe.checkout.Session.create(
        line_items = [
            {
                'price': stripe_price_obj.id,
                'quantity': 1,
            }
        ],
        mode = 'payment',
        success_url = success_url,
        cancel_url = cancel_url
    )
    return checkout_session.url