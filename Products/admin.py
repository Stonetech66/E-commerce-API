from django.contrib import admin
from .models import Coupon, Product, Order, OrderProduct, Review, Category, Address, payment, Refund, Variation, ProductVariation
# Register your models here.

class Variationinline(admin.TabularInline):
    model=Variation
    extra=1


class ProductVariationinline(admin.TabularInline):
    model=ProductVariation
    extra=1

class ProductAdmin(admin.ModelAdmin):
    inlines=[Variationinline, ]
    list_display=["name", "price", ]
    list_filter=["price", "category"]


def make_refund_granted(modeladmin, request,queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_granted.short_description="Update refund to granted"

def  order_being_delivered(modeladmin, request, queryset ):
    queryset.update(being_delivered=True)
order_being_delivered.short_description="Update order to being delivered"

def  order_recieved(modeladmin, request, queryset ):
    queryset.update(being_delivered=False, recieved=True)
order_recieved.short_description="Update order to recieved"


class OrderAdmin(admin.ModelAdmin):
    list_display=["user", "ordered",    "being_delivered",
    "recieved",
    "refund_requested",
    "refund_granted",
    "ref_code",
    "payment",
    "billing_address",
    "coupon"]

    list_filter=["ordered",
    "being_delivered",
    "recieved",
    "refund_requested",
    "refund_granted",
    "coupon"
    ]
    search_fields=[
        "user__email",
        "ref_code",
        "coupon"
    ]
    list_display_links=[
        "user",
        "billing_address",
        "payment",
        "coupon"
    ]
    actions=[make_refund_granted, order_being_delivered, order_recieved]

class VariationAdmin(admin.ModelAdmin):
    list_display=["name", "product"]
    inlines=[ProductVariationinline]
class PaymentAdmin(admin.ModelAdmin):
    list_display=["user", "payment_id", "date_paid"]

class AddressAdmin(admin.ModelAdmin):
    list_display=[
        "user",
        "zip",
        "country",
        "save_as_default"
    ]

class CouponAdmin(admin.ModelAdmin):
    list_display=[
        "code",
        "amount",
        "active",
    ]

def activate_coupon(modeladmin,request, queryset):
    queryset.update(active=True)

activate_coupon.short_description="Activate coupon"

def deactivate_coupon(modeladmin, request, queryset):
    queryset.update(active=False)

deactivate_coupon.short_description= "deactivate coupon"

class CouponAdmin(admin.ModelAdmin):
    list_display=["code", "active", "amount"]
    list_filter=["active"]
    actions=[activate_coupon, deactivate_coupon]




admin.site.register(Product, ProductAdmin)
admin.site.register(OrderProduct)
admin.site.register(Refund)
admin.site.register(Category)
admin.site.register(Review)
admin.site.register(Address, AddressAdmin)
admin.site.register(Order,OrderAdmin)
admin.site.register(Coupon, CouponAdmin)
admin.site.register(payment,PaymentAdmin)
admin.site.register(Variation, VariationAdmin)
admin.site.register(ProductVariation)


