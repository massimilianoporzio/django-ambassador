import stripe
from django.db import transaction
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import exceptions
from .serializers import LinkSerializer
from core.models import Link, Order, Product, OrderItem
import decimal
from django.core.mail import send_mail


class LinkAPIView(APIView):

    def get(self, _, code=''):
        link = Link.objects.filter(code=code).first()  # così rest lista vuota se non esiste link con quel 'code'
        # try:
        #     link = Link.objects.get(code=code)
        # except Link.DoesNotExist:
        #     raise exceptions.APIException("link not found")
        serializer = LinkSerializer(link)
        return Response(serializer.data)


class OrderAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        link = Link.objects.filter(code=data['code']).first()
        if not link:
            raise exceptions.APIException('Invalid code!')

        try:
            order = Order()  # creo ordine
            # DATI PRESI DAL LINK (il carrello)
            order.code = link.code
            order.user_id = link.user.id
            order.ambassador_email = link.user.email
            # ===========================
            # DATI PRESI DALLA RICHIESTA POST (dal front-end)
            order.first_name = data['first_name']
            order.last_name = data['last_name']
            order.email = data['email']
            order.address = data['address']
            order.country = data['country']
            order.city = data['city']
            order.zip = data['zip']
            # salvo su db ma nella trnsazione
            order.save()

            # preparo lista di items dell'ordine CON I DATI -  lista di oggetti json
            line_items = []
            for item in data['products']:
                product = Product.objects.filter(pk=item['product_id']).first()
                quantity = decimal.Decimal(item['quantity'])

                order_item = OrderItem()  # creo item
                order_item.order = order
                order_item.product_title = product.title
                order_item.price = product.price
                order_item.quantity = quantity
                order_item.ambassador_revenue = decimal.Decimal(.1) * product.price * quantity
                order_item.admin_revenue = decimal.Decimal(.9) * product.price * quantity
                order_item.save()  # SALVO l'item dell'ordine

                line_items.append({
                    'name': product.title,
                    'description': product.description,
                    'images': [
                        product.image
                    ],
                    'amount': int(100 * product.price), #in centesimi di dollaro (per stripe)
                    'currency': 'usd',
                    'quantity': quantity
                })
            stripe.verify_ssl_certs = False
            stripe.api_key = "sk_test_B9N7bDJ1lEt8ey2GZ72qCCor"
            source = stripe.checkout.Session.create(
                success_url='http://localhost:5000/success?source={CHECKOUT_SESSION_ID}', #URL DEL FRONTEND
                cancel_url='http://localhost:5000/error',
                payment_method_types=['card'],
                line_items=line_items
            )
            order.transaction_id = source['id'] #id della transazione di stripe
            order.save()

            return Response(source)
        except Exception:
            transaction.rollback()
            return Response({
                'message': "Error occurred"
            })

class OrderConfirmAPIView(APIView):
    def post(self, request):
        order = Order.objects.filter(transaction_id=request.data['source']).first()
        if not order:
            raise exceptions.APIException('Order not found!')

        order.complete = 1
        order.save()

        # Admin Email
        send_mail(
            subject='An Order has been completed',
            message='Order #' + str(order.id) + 'with a total of $' + str(order.admin_revenue) + ' has been completed!',
            from_email='from@email.com',
            recipient_list=['admin@admin.com','massimiliano.porzio@gmail.com']
        )

        send_mail(
            subject='An Order has been completed',
            message='You earned $' + str(order.ambassador_revenue) + ' from the link #' + order.code,
            from_email='from@email.com',
            recipient_list=[order.ambassador_email,"massimiliano.porzio@gmail.com"]
        )

        return Response({
            'message': 'success'
        })

