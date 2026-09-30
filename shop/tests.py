import pytest

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from shop.models import Product, Category, Cart, CartItem, Order

# Create your tests here.
User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()



def auth_user():
    return User.objects.create_user(phone_number="09014862969")



def sample_product():
    category = Category.objects.create(name="لپ تاپ", slug='laptop')
    return Product.objects.create(
        title='لپ تاپ گیمینگ',
        slug='gaming-laptop',
        category=category,
        price=2000,
        inventory=5,
        is_active=True

    )
@pytest.mark.django_db
class TestShopFlow:
    @pytest.fixture
    def test_get_product_list_allow_any(self, api_client, sample_product):
        """تست دریافت عمومی محصولات بدون نیاز به لاگین"""
        url = "/api/v1/shop/products/"
        response = api_client.get(url, follow=True)
        assert response.status_code == status.HTTP_200_OK

    @pytest.fixture
    def test_add_to_cart_authenticated(self, api_client, auth_user, sample_product):
        """تست افزودن به سبد خرید برای کاربر احراز هویت شده"""
        api_client.force_authenticate(user=auth_user)
        url = "/api/v1/shop/cart/"
        payload = {"product_id": sample_product.id, "quantity": 2}
        response = api_client.post(url, payload, format="json", follow=True)
        assert response.status_code == status.HTTP_200_OK

        cart = Cart.objects.get(user=auth_user)
        assert cart.items.count() == 1
        assert cart.items.first().quantity == 2

    @pytest.fixture
    def test_checkout_reduces_inventory(self, api_client, auth_user, sample_product):
        """تست تسویه حساب و کسر موجودی از انبار"""
        api_client.force_authenticate(user=auth_user)

        cart = Cart.objects.create(user=auth_user)
        CartItem.objects.create(cart=cart, product=sample_product, quantity=3)

        url = "/api/v1/shop/checkout/"
        response = api_client.post(url, follow=True)
        assert response.status_code == status.HTTP_201_CREATED

        order = Order.objects.get(user=auth_user)
        assert order.total_price == 3 * sample_product.price

        sample_product.refresh_from_db()
        assert sample_product.inventory == 2
    @pytest.mark.django_db
    def test_checkout_fails_on_insufficient_inventory(self, api_client, auth_user, sample_product):
        """تست خطای موجودی ناکافی"""
        api_client.force_authenticate(user=auth_user)

        cart = Cart.objects.create(user=auth_user)
        CartItem.objects.create(cart=cart, product=sample_product, quantity=6)

        # دقت کن: /api/v1/shop/checkout/ (نه apiv1)
        url = "/api/v1/shop/checkout/"
        response = api_client.post(url, follow=True)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Order.objects.count() == 0
#
# @pytest.fixture
# def auth_client():
#     client = APIClient()
#     user = User.objects.create_user(phone_number='09014862969')
#     client.force_authenticate(user=user)
#     return client, user
#
# def auth_user():
#     return
#
# @pytest.mark.django_db
# class TestOrderCheckout:
#     def test_checkout_reduces_inventory(self, auth_client):
#         client, user = auth_client:
#         category = Category.objects.create(name='الکترونیک', slug='elec')
#         product = Product.objects.create(
#             title='لب تاب تست',
#             slug='test-laptop',
#             category=category,
#             price=2000000,
#             inventoty=4,
#             is_active=True
#         )
#
#         cart = Cart.objects.create(user=user)
#         CartItem.objects.create(cart=cart, product=product, quantity=2)
#         checkout_url = reverse('checkout')
#         response = client.post(checkout_url)
#
#         assert response.status_code == 201
#
#         product.refresh_from_db()
#         assert product.inventory == 3
#         assert cart.item.count() == 0
