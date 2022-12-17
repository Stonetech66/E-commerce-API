
import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.urls import reverse
from  .countries import Countries

from Users.models import MyUser

Address_choices=[
    ("S", "Shipping Address"),
    ("B", "Billing address")
]

# Create your models here.
class Coupon(models.Model):
    code=models.CharField(max_length=20, unique=True)
    description=models.TextField()
    amount=models.DecimalField(max_digits=10000, decimal_places=2)
    active=models.BooleanField(default=False)

    def __str_(self):
        return self.code

class Address(models.Model):
    user=models.ForeignKey(MyUser, on_delete=models.CASCADE)
    address= models.CharField(max_length=1000)
    country= models.CharField(choices=Countries, max_length=100000)
    zip= models.CharField(max_length=10000)
    # address_type= models.CharField(max_length=1000, choices=Address_choices)
    save_as_default=models.BooleanField(default=False)


    class Meta:
        verbose_name_plural= "Addresses"

    def __str_(self):
        return self.user
    
    def get_absolute_url(self):
        return reverse("address-update", args=[str(self.id)])


 
class payment(models.Model):
    user= models.ForeignKey(MyUser, on_delete=models.SET_NULL, null=True)
    payment_id= models.CharField(max_length=30)
    amount=models.FloatField()
    date_paid= models.DateTimeField(auto_now_add=True)


    class Meta:
        ordering=["-date_paid"]

    def __str__(self):
        return f"{self.user.email}"


   

class Category(models.Model):
    name= models.CharField(max_length=1000)
    slug= models.SlugField(unique=True, editable= False, max_length=1000)

    def clean(self):
        if Category.objects.filter(name__iexact=self.name):
            raise ValidationError("Category already exists")

    def save(self, *args, **kwargs):
        self.slug= slugify(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("category-detail", args=[str(self.slug)])
    def __unicode__(self):
        return self.name
    
    class Meta:
        verbose_name_plural= "Categories"



class Product(models.Model):
    id= models.UUIDField(editable=False, primary_key=True, default=uuid.uuid4)
    name=models.CharField(max_length=200)
    price= models.DecimalField(decimal_places=2, max_digits=10000000)
    description= models.TextField()
    discount_price= models.DecimalField(decimal_places=2, max_digits=10000000, null=True, blank=True)
    category= models.ManyToManyField(Category, related_name="category")
    brand= models.CharField(max_length=1000, null=True, blank=True)
    img= models.ImageField(null=True, blank=True, upload_to="images/")




    def  __str__(self):
        return f"{self.name}"
    
    def get_add_to_cart_url(self):
        return reverse("add_cart", kwargs={"pk":self.id})


    def get_absolute_url(self):
        return reverse("product-detail", args=[str(self.id)])

class Review(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    user=models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="user_reviews")
    body= models.TextField()
    date_added=models.DateField(auto_now_add=True)

    class Meta:
        unique_together=("product", "user")
        ordering=["-date_added"]

    def __str__(self):
        return f"{self.product.name} {self.body[:30]}"
class Variation(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variation_class")
    name=models.CharField(max_length=50)

    class Meta:
        unique_together=(
            "product", "name"
        )

    def __str__(self):
        return self.name

class ProductVariation(models.Model):
    value=models.CharField(max_length=50)
    variation=models.ForeignKey(Variation, on_delete=models.CASCADE, related_name="variations")
    image=models.ImageField(null=True, blank=True)

    class Meta:
        unique_together=(
            "value", "variation"
        )

    def __str__(self):
        return self.value


class OrderProduct(models.Model):
    user= models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="user_order")
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    qty= models.PositiveIntegerField(default=1)
    ordered= models.BooleanField(default= False)
    variation= models.ManyToManyField(ProductVariation, related_name="variations")
    def __str__(self):
        return self.user.email

    def get_total_price(self):
        return self.product.price * self.qty

    def get_total_discount_price(self):
        return self.product.discount_price * self.qty

    def get_final_price(self):
        if self.product.discount_price:
            return self.get_total_discount_price()
        return self.get_total_price()


class Order(models.Model):
    user=models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="user_orders")
    ordered=models.BooleanField(default=False)
    order_date=models.DateTimeField(auto_now_add=True)
    item=models.ManyToManyField(OrderProduct)
    billing_address= models.ForeignKey(Address,related_name="billing" , null=True, on_delete=models.SET_NULL)
    shipping_address= models.ForeignKey(Address, related_name="shipping", null=True ,on_delete=models.SET_NULL)
    payment=models.OneToOneField(payment, on_delete=models.SET_NULL, null=True)
    being_delivered=models.BooleanField(default=False)
    recieved=models.BooleanField(default=False) 
    refund_requested=models.BooleanField(default=False)
    refund_granted=models.BooleanField(default=False)
    ref_code= models.CharField(max_length=20, null=True, blank=True)
    coupon=models.ForeignKey(Coupon, null=True, on_delete=models.SET_NULL, related_name="Order_coupon", blank=True)


    def __str_(self):
        return self.user

    def get_total(self):
        total=0
        for i in self.item.all():
            total += i.get_final_price()
        if self.coupon:
            return total-self.coupon.amount
        return total

    def get_total_quantity(self):
        total=0
        for i in self.item.all():
            total += i.qty

        return total


class Refund(models.Model): 
    user=models.ForeignKey(MyUser, on_delete=models.CASCADE)
    order=models.ForeignKey(Order, on_delete=models.CASCADE)
    message= models.CharField(max_length=200)
    email=models.EmailField()
    accepted=models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email}-{self.pk}"
    


