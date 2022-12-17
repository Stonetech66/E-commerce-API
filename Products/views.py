from django.conf import settings
from django.shortcuts import render
from Users.models import MyUser
from .serializers import (AddAddressToOrderSerializer, 
AddressCreateSerializer, AddressSerializer, CategorySerializer, 
CouponSerializer, OrderSerializer, PaymentHistorySerializer, 
Product_Serializer, CategoryListSerializer, RefundSerializer,
 Productlist_serializer, ReviewSerializer, UserProfileSerializer, Add_To_Cart_Serializer, Remove_from_carts)
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Address, Category, Coupon, Order, OrderProduct, Product, Refund, Review, Variation
from Users.models import  UserProfile
import stripe
from .models import payment
import random, string
from django.views.decorators.csrf import csrf_exempt
stripe.api_key=settings.STRIPE_SECRET_TEST_KEY
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
# Create your views here.


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))




class ProductView(generics.ListAPIView):

    serializer_class= Productlist_serializer
    filter_backends=[filters.SearchFilter, filters.OrderingFilter]
    ordering_fields=['price']
    search_fields=["name", "brand"]
    permission_classes= []

    def get_queryset(self):
        return Product.objects.all()



class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=Product_Serializer
    permission_classes=[permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        return Product.objects.all().prefetch_related("category", "variation_class", "variation_class__variations")
    
    def get_object(self):
        pk=self.kwargs["pk"]
        return get_object_or_404(Product, pk=pk)


class Add_to_cart(APIView):


    serializer_class=Add_To_Cart_Serializer

    def get_serializer(self):
        return Add_To_Cart_Serializer()
    def post(self, request, *args, **kwargs):
        p=self.kwargs['pk']
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            product=get_object_or_404(Product, id=p)
            v= serializer.validated_data.get('variations')
            variation=Variation.objects.filter(product__id=product.id).count()
            if len(v) < variation:
                return Response({"error": "incomplete variations added"}, status=status.HTTP_400_BAD_REQUEST)

            for i in v:
                o_p=OrderProduct.objects.filter(user=request.user,ordered=False, variation=i, product=product)
            if o_p.exists():
                o_p=o_p.last()
                o_p.qty = serializer.validated_data.get('qty')
                o_p.save()
                return Response({"message":"your cart has been updated"})
            else:
                try:
                    o_p=OrderProduct.objects.create(user=request.user, ordered=False, product=product)
                    o_p.variation.add(*v)
                    o_p.qty=serializer.validated_data.get('qty')
                    o_p.save()
                except:
                    return Response({'error': 'variation not found'}, status=status.HTTP_404_NOT_FOUND)
            order=Order.objects.filter(user=request.user,ordered=False)
            if order.exists():
                o=order.last()   
                if not o.item.filter(product__id=o_p.id).exists():
                    o.item.add(o_p)
                    o.save()
                    return Response({"message":"item added to cart"}, status=status.HTTP_200_OK)
            else:
                order=Order.objects.create( user=request.user,ordered=False)
                order.item.add(o_p)
                order.save()
                return Response({"message":"item added to your cart"})
        
class CartView(generics.RetrieveAPIView):
    serializer_class=OrderSerializer

    def get_object(self):

        try:
            return Order.objects.get(user=self.request.user, ordered=False)
        except:
            return Order.objects.create(user=self.request.user, ordered=False)



class StripePaymentView(APIView):
    def post(self, request,*args, **kwargs):
        def post(self, *args, **kwargs):
            try:
                order= Order.objects.get(user=self.request.user, ordered=False)
                if not order.shipping_address:
                    return Response({"error":"You have nnot attached a shipping address to this order "}, status=status.HTTP_400_BAD_REQUEST)
                amount= int(order.get_total()*100)
                customer=stripe.Customer.create(email= self.request.user.email)
                intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                customer=customer["id"],
    )

                return Response({
                    'clientSecret': intent['client_secret']
                })
            except stripe.error.CardError as e:
                return Response("A payment error occurred: {}".format(e.user_message))
            except stripe.error.RateLimitError:
                return Response("Too many requests try again later")
            except stripe.error.InvalidRequestError:
                return Response("invalid parameters")
            except stripe.error.StripeError:
                return Response("something went wrong. You were not charged please try again")
            except stripe.error.ApiConnectionError:
                return Response("Network error please try again later")
            except Exception:
                return Response("A serious error occured we have been notified please try again later")


@csrf_exempt
def stripe_webhook(request):
    payload= request.body
    sig_header=request.META['HTTP_STRIPE_SIGNATURE']
    event=None
    try:
        event= stripe.Webhook.construct_event(
            payload,sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'payment_intent.succeeded':
        intent= event['data']['object']
        stripe_customer_id=intent['customer']
        stripe_customer=stripe.Customer.retrieve(stripe_customer_id)
        customer_email=stripe_customer["email"]
        order=Order.objects.get(user__email=customer_email, ordered=False)
        Payment= payment(user=order.user, payment_id=intent["id"], amount=intent["amount"])
        Payment.save()
        order_item= order.item.all()
        for i in order_item:
            i.ordered=True
            i.save()
        order.payment=Payment
        order.ref_code= create_ref_code()
        order.ordered=True
        order.save()
        return Response({"message":"Payment successful check your profile to monitor your order"}, status=status.HTTP_202_ACCEPTED)
    return Response({"message": "error during payment please try again dont worry you have not been charged"}, status=status.HTTP_202_ACCEPTED)
    

class Remove_from_cart(APIView):

    serializer_class=Remove_from_carts

    def get_serializer(self):
        return Remove_from_carts()
    
    def post(self, request, *args, **kwargs):
        serializer=self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):

            pk=self.kwargs['pk']
            v=request.data.get("variations", [])
            product= get_object_or_404(Product, pk=pk)
            variation=Variation.objects.filter(product__id=product.id).count()
            if len(v) < variation:
                return Response({"error": "incomplete variations added"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                for i in v:
                    k= OrderProduct.objects.get(user=request.user, product=product, ordered=False, variation=i)
            except:
                    return Response({"message":"item not in your cart"}, status=status.HTTP_400_BAD_REQUEST)
            # p= Order.objects.filter(user=request.user, item=k, ordered=False)
            # if p.exists():
            if k :
                k.delete()
                return Response({"message":"your cart has been updated"}, status=status.HTTP_200_OK)

            else:
                return Response({"message":"your cart has been updated"}, status=status.HTTP_200_OK)

# class Reduce_quantity(APIView):
#     def post(self, request, *args, **kwargs):
#         pk=request.data.get("id", None)
#         v=request.data.get("variations", [])
#         product= get_object_or_404(Product, pk=pk)
#         variation=Variation.objects.filter(product__id=product.id).count()
#         if len(v) < variation:
#             return Response({"error": "incomplete variations added"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             for i in v:
#                 o= OrderProduct.objects.get( product=product, ordered=False, variation=i, user=request.user)
#         except:
#             return Response({"message":"invalid request this item is not in your cart"})
#         try:
#             i=Order.objects.get(ordered=False, user=request.user)
#         except:
#             return Response({"message":"You do not have an active order"},status=status.HTTP_400_BAD_REQUEST)

#         if i.item.filter(product=product, ordered=False, user=request.user):
#             o.qty -= 1
#             o.save()    
#             if o.qty <1:
#                         o.delete()
#                         return Response({"message":"Your cart has been updated"},status=status.HTTP_200_OK)
#             return Response({"message":"Your cart has been updated"}, status=status.HTTP_200_OK)

#         else:
#             return Response({"message":"item not in your cart"},status=status.HTTP_400_BAD_REQUEST)

            
class CategoryListView(generics.ListAPIView):
    """
List all categories 
    """
    serializer_class=CategoryListSerializer
    queryset=Category.objects.all()
    permission_classes= []


class CategoryDetailView(generics.RetrieveAPIView):
    serializer_class=CategorySerializer
    lookup_field="slug"
    permission_classes=[]
    
    def get_queryset(self):
        return Category.objects.all().prefetch_related("category")


class RefundView(APIView):

    def post(self, request, *args, **kwargs):
        serializer=RefundSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                a=serializer.validated_data.get("Order_ref_code")
                p=serializer.validated_data.get("email")
                v=serializer.validated_data.get("message")
                c=Order.objects.get(ref_code=a,user=request.user, ordered=True)
                if c:
                    serializer.validated_data.pop("Order_ref_code")
                    serializer.save(message=v, email=p, user=request.user, order=c)
                    c.refund_requested=True
                    c.save()
                    return Response(serializer.data,{"message":"Your request has been recieved we will be in touch with the email you provided"}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"This order does not exists please check  Order_ref_code and try again"}, status=status.HTTP_404_NOT_FOUND)

        

class CouponView(APIView):
    def post(self, request, *args,**kwargs):
        serializer=CouponSerializer(data=request.data)
        try:
            p=Order.objects.get(ordered=False)
        except:
            return Response({"message":"You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)
        if p.coupon !=None:
            return Response({"message":"You already have a coupon activated"}, status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            code=serializer.validated_data.get("code")
            if code == None:
                return Response({"message":"invalid request recieved"}, status=status.HTTP_400_BAD_REQUEST)
            try:
                c=Coupon.objects.get(code=code, active=True)
                p=Order.objects.get(ordered=False, user=request.user)
                if c:
                    p.coupon=c
                    p.save()
                    return Response({"message":"coupon sucessfully added to order"}, status=status.HTTP_200_OK)
            except:
                return Response({"message":"This coupon is not valid"}, status=status.HTTP_404_NOT_FOUND)


class AddressListView(generics.ListAPIView):
    serializer_class= AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressCreateView(generics.CreateAPIView):
    serializer_class=AddressCreateSerializer
    queryset=Address.objects.all()

    def perform_create(self, serializer):
        p= serializer.validated_data.get("Use_default_shipping_address")
        if p == True:
            try:
                a=Address.objects.get(user=self.request.user, save_as_default=True)
                o=Order.objects.filter(user=self.request.user, ordered=False)
                if o.exists():
                    o=o.last()
                    o.shipping_address= a
                    o.save()
                    return Response({"message":" Your address has been added to your order"}, status=status.HTTP_200_OK )
                else:
                    return Response({"message":"You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({"message":"You do not have a default address"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.validated_data.pop("Use_default_shipping_address")
            try:
                o=Order.objects.get(user=self.request.user, ordered=False)
            except:
                return Response({"message":"You do not have an active order"}, status=status.HTTP_400_BAD_REQUEST)
            if Address.objects.filter(user=self.request.user).exists():
                if serializer.validated_data.get("save_as_default") == True:
                    p=Address.objects.filter(user=self.request.user, save_as_default=True)
                    if p.exists():
                        j=p.last()
                        j.save_as_default = False
                        j.save()
                o_a=serializer.save(user=self.request.user)
                o.shipping_address= o_a
                o.save()
                return o_a
            else:
                o_a=serializer.save(user=self.request.user, save_as_default=True)
                o.shipping_address=o_a
                o.save()
                return o_a

class DefaultAddress(generics.RetrieveUpdateAPIView):
    serializer_class=AddressCreateSerializer
    permission_classes=[permissions.IsAuthenticated]

    def get_object(self):
        try:

            return Address.objects.get(user=self.request.user, save_as_default=True)
        
        except:
            return Response({"message":"You do not have a default address"}, status=status.HTTP_400_BAD_REQUEST)



class UpdateDeleteAddress(generics.RetrieveUpdateDestroyAPIView):
    serializer_class=AddressSerializer

    def get_queryset(self):
        return Address.objects.all().filter(user=self.request.user)


class AddAddressToOrder(APIView):
    def post(self, request, *args, **kwargs):
        serializer=AddAddressToOrderSerializer(data=request.data)
        if serializer.is_valid():
            p=serializer.validated_data.get("id")
            address= Address.objects.filter(id=p, user=request.user)
            o=Order.objects.filter(ordered=False, user=request.user)
            if not address.exists():
                return Response({"error":"this address does not exists"}, status=status.HTTP_404_NOT_FOUND)
            if not o.exists():
                return Response({"error":"You do not have a active order"}, status=status.HTTP_400_BAD_REQUEST)
            order=o.last()
            order.shipping_address=address.last()
            order.save()
            return Response({"message":"shipping address sucessfullly added to order"}, status=status.HTTP_200_OK)



class UserProfileView(generics.ListAPIView):
    serializer_class= UserProfileSerializer
    queryset=UserProfile.objects.all()



class OrderHistory(generics.ListAPIView):
    serializer_class=PaymentHistorySerializer

    def get_queryset(self):
        return payment.objects.filter(user=self.request.user).select_related("order", "order__shipping_address")


class ReviewCreate(APIView):

    def post(self, request, *args, **kwrags):
        serializer= ReviewSerializer(data=request.data)
        if serializer.is_valid():
            p=serializer.validated_data.get("product")
            user=self.request.user
            if not user.user_orders.filter(ordered=True).filter(item__product__id=p.id).exists():
                return  Response({"message":"You have not ordered this product so you cant give a review"}, status=status.HTTP_403_FORBIDDEN)
            if  Review.objects.filter(user=user, product=p).exists():
                return Response({"message":"You  already have a review on this order"}, status= status.HTTP_400_BAD_REQUEST)
            
            else:
                serializer.save(user=self.request.user)
                return Response({"message":"Review sucessfully added"}, status=status.HTTP_200_OK)


