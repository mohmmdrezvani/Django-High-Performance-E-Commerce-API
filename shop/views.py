from django.db import transaction
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem, Order, OrderItem, Product
from .payment import send_payment_request
from .serializers import CartSerializer, ProductListSerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ['category__slug', 'is_active']
    search_fields = ['title']
    ordering_fields = ['price', 'created_at']

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related('category').order_by('-created_at')

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class CartView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        cart = Cart.objects.prefetch_related('items__product').get(id=cart.id)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    def post(self, request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = Product.objects.filter(id=product_id, is_active=True).first()
        if not product:
            return Response({'detail': 'محصول یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        if product.inventory < quantity:
            return Response({'detail': 'موجودی کالا کافی نیست.'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        return Response({'detail': 'به سبد خرید اضافه شد.'}, status=status.HTTP_200_OK)


class CheckoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        cart = Cart.objects.prefetch_related('items__product').filter(user=request.user).first()
        if not cart or not cart.items.exists():
            return Response({'detail': 'سبد خرید خالی است.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            total_price = 0
            product_ids = [item.product_id for item in cart.items.all()]
            locked_products = {
                p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
            }

            for item in cart.items.all():
                prod = locked_products.get(item.product_id)
                if prod.inventory < item.quantity:
                    return Response(
                        {'detail': f'موجودی محصول {prod.title} در این لحظه کافی نیست.'},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                total_price += prod.price * item.quantity

            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                status='pending'
            )

            order_items = []
            for item in cart.items.all():
                prod = locked_products[item.product_id]
                prod.inventory -= item.quantity
                prod.save()

                order_items.append(OrderItem(
                    order=order,
                    product=prod,
                    price=prod.price,
                    quantity=item.quantity
                ))

            OrderItem.objects.bulk_create(order_items)
            cart.items.all().delete()

        return Response({'detail': 'سفارش ثبت شد.', 'order_id': order.id}, status=status.HTTP_201_CREATED)


class PaymentRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, order_id):
        order = Order.objects.filter(id=order_id, user=request.user, status='pending').first()
        if not order:
            return Response(
                {'detail': 'سفارش یافت نشد یا قبلاً تعیین وضعیت شده است.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        payment_url, err = send_payment_request(order, request.user.phone_number)
        if payment_url:
            return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
        return Response(
            {'detail': 'خطا در اتصال به درگاه پرداخت', 'errors': err},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PaymentVerifyView(APIView):
    # کال‌بک درگاه بانکی برای همه کاربران (ریدایرکت مرورگر) در دسترس است
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')

        if not authority:
            return Response({'detail': 'شناسه تراکنش یافت نشد.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            try:
                order = Order.objects.select_for_update().get(authority=authority)
            except Order.DoesNotExist:
                return Response({'detail': 'سفارش یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

            # الگوی Idempotency: در صورت چندبار فراخوانی یا رفرش صفحه
            if order.is_paid:
                return Response({'detail': 'این تراکنش قبلاً با موفقیت تایید شده است.', 'order_id': order.id})

            if payment_status == 'OK':
                order.is_paid = True
                order.status = 'processing'
                order.save()
                return Response({'detail': 'پرداخت با موفقیت تایید شد.', 'order_id': order.id})
            else:
                order.status = 'canceled'
                order.save()
                return Response({'detail': 'تراکنش ناموفق بود یا لغو شد.'}, status=status.HTTP_400_BAD_REQUEST)
