from dataclasses import fields
from rest_framework import serializers, response, status
from .models import Address, Category, Order, OrderProduct, Product, Refund, Review, payment
from Users.models import UserProfile


class Product_reviews(serializers.Serializer):
    username=serializers.CharField(source="user.Fullname", read_only=True)
    body=serializers.CharField()
    date_added=serializers.DateField()

class ProductVariationSerializer(serializers.Serializer):
    variation=serializers.CharField()
    id=serializers.IntegerField()
    value=serializers.CharField()
    image=serializers.ImageField()

class VariationSerializer(serializers.Serializer):
    id=serializers.IntegerField()
    name=serializers.CharField(read_only=True)
    values=ProductVariationSerializer(source="variations", many=True, read_only=True)


class AddressSerializer(serializers.ModelSerializer):
    url=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=Address
        fields= ["id", "url", "address", "country", "zip", "save_as_default"]

    def get_url(self, obj):
        return obj.get_absolute_url()

class Product_Serializer(serializers.ModelSerializer):
    Category=serializers.StringRelatedField(many=True, source="category", read_only=True)
    variations=VariationSerializer(source="variation_class", many=True, read_only=True)
    reviews=Product_reviews(source="reviews.all", read_only=True, many=True)
    class Meta:
        model=Product
        fields=[
            "id",
            "name",
            "price",
            "discount_price",
            "img",
            "category",
            "Category",
            "brand",
            "variations",
            "description",
            "reviews"
        ]


class Productlist_serializer(serializers.ModelSerializer):
    product_url=serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=Product
        fields=[
            "id",
            "name",
            "price",
            "discount_price",
            "img",
            "product_url",

        ]
    def get_product_url(self, obj):
        return obj.get_absolute_url()


class OrderProductSerializer(serializers.ModelSerializer):
    product=Productlist_serializer(read_only=True)
    sub_total_price=serializers.SerializerMethodField(read_only=True)
    variation=ProductVariationSerializer(many=True, read_only=True)
    class Meta:
        model=OrderProduct
        fields=[
            "id",
            "product",
            "qty",
            "sub_total_price",
            "variation"
        ]
    
    def get_sub_total_price(self,obj):
        return obj.get_final_price()




class UserOrderProductSerializer(serializers.ModelSerializer):
    product=Productlist_serializer(read_only=True)
    variation=ProductVariationSerializer(many=True, read_only=True)
    class Meta:
        model=OrderProduct
        fields=[
            "id",
            "product",
            "qty",
            "sub_total_price",
            "variation"
        ]




class OrderSerializer(serializers.ModelSerializer):
    items=OrderProductSerializer(many=True, read_only=True, source="item")
    total_price= serializers.SerializerMethodField(read_only=True)
    class Meta:
        model=Order
        fields=[
        "id",
        "items",
        "total_price"


        ]
    def get_total_price(self,obj):
        return obj.get_total()

class UserOrderSerializer(serializers.ModelSerializer):
    items=OrderProductSerializer(many=True, read_only=True, source="item")
    shipping_address=AddressSerializer(read_only=True)
    class Meta:
        model=Order
        fields=[
        "id",
        "items",
        "being_delivered",
        "recieved",
        "ref_code",
        "shipping_address"


        ]

class CategorySerializer(serializers.ModelSerializer):
    products=Productlist_serializer(many=True, read_only=True, source="category")
    class Meta:
        model=Category
        fields=[
            "name",
            "products"
        ]

class CategoryListSerializer(serializers.ModelSerializer):
    category_url=serializers.SerializerMethodField()
    class Meta:
        model=Category
        fields=[
            "name",
            "category_url"
        ]
    
    def get_category_url(self, obj):
        return obj.get_absolute_url()
class RefundSerializer(serializers.ModelSerializer):
    Order_ref_code=serializers.CharField(write_only=True)
    class Meta:
        model=Refund
        fields=[
            "Order_ref_code",
            "email",
            "message"
        ]


class CouponSerializer(serializers.Serializer):
    code=serializers.CharField()



class AddressCreateSerializer(serializers.ModelSerializer):
    Use_default_shipping_address=serializers.BooleanField(required=False)
    class Meta:
        model=Address
        fields= ["id", "address", "country", "zip", "save_as_default", "Use_default_shipping_address"]



"""
Dont Forget to change this
"""
class UserProfileSerializer(serializers.ModelField):
 
    class Meta:
        model=UserProfile
        fields=[
            "profile_pic",
        ]


class PaymentHistorySerializer(serializers.ModelSerializer):
    order=UserOrderSerializer(read_only=True)
    class Meta:
        model=payment
        fields=[
            "order",
            "amount",
            "date_paid"
        ]

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model=Review
        fields=[
            "product",
            "body"
        ]



class Add_To_Cart_Serializer(serializers.Serializer):
    qty=serializers.IntegerField()
    variations=serializers.ListField(child=serializers.IntegerField())



        


class AddAddressToOrderSerializer(serializers.Serializer):
    id=serializers.IntegerField()

class Remove_from_carts(serializers.Serializer):
    variations=serializers.ListField(child=serializers.IntegerField())
