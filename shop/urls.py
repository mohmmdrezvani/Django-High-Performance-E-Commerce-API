from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, CartView, CheckoutView, PaymentRequestView, \
    PaymentVerifyView

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
                  path('cart/', CartView.as_view(), name='cart'),
                  path('checkout/', CheckoutView.as_view(), name='checkout'),
                  path('payment/request/<int:order_id>/', PaymentRequestView.as_view(), name='payment-request'),
                  path('payment/verify/', PaymentVerifyView.as_view(), name='payment-verify')
              ] + router.urls
