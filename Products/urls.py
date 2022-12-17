from django.urls import path, include
from . import views
from dj_rest_auth.views import PasswordResetView, PasswordResetConfirmView
from rest_framework.documentation import include_docs_urls


from rest_framework.schemas import get_schema_view

from rest_framework.documentation import include_docs_urls
from rest_framework_swagger.views import get_swagger_view


API_TITLE=" STONE E-commerce API"
schema_view=get_swagger_view(title=API_TITLE)


urlpatterns=[
    path("", views.ProductView.as_view(), name="product-list"),
    path("<uuid:pk>/", views.ProductDetailView.as_view(), name="product-detail"),
    path("add-to-cart/<uuid:pk>/", views.Add_to_cart.as_view(), name="add-to-cart"),
    path("cart/", views.CartView.as_view(), name="user-cart"),
    path("payment/", views.StripePaymentView.as_view(), name="payment"),
    path("payment/webhook/", views.stripe_webhook, name="stripe-webhook"),
    path("category/", views.CategoryListView.as_view(), name="category-list"),
    path("<slug:slug>/!", views.CategoryDetailView.as_view(), name="category-detail"),
    path("request-refund/", views.RefundView.as_view(), name="refund"),
    path("remove-from-cart/<uuid:pk>/", views.Remove_from_cart.as_view(), name="remove-cart"),
    # path("reduce-qty/", views.Reduce_quantity.as_view(), name="reduce-cart"),
    path("add-coupon/", views.CouponView.as_view(), name="add-coupon"),
    path("address/create/", views.AddressCreateView.as_view(), name="address-create"),
    path("address/", views.AddressListView.as_view(), name="address-list"),
    path("address/default", views.DefaultAddress.as_view(), name="address-list"),
    path('', include('dj_rest_auth.urls')),
    path('signup/', include('dj_rest_auth.registration.urls')),
    path("order-history/", views.OrderHistory.as_view(), name="user-orders"),
    path('password/reset/', PasswordResetView.as_view()),
    path("docs/", schema_view, name="schema"),
    path("address/<int:pk>/", views.UpdateDeleteAddress.as_view(), name="address-update"),
    path("add-address/", views.AddAddressToOrder.as_view(), name="add-address"),
    path("review/", views.ReviewCreate.as_view(), name="review-create"),
    path("password/reset/confirm/<uidb64>/<token>/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]