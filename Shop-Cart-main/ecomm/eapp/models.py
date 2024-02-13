from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=50)
    email=models.EmailField()
    desc=models.TextField(max_length=500)
    phonenumber=models.IntegerField()

    def __str__(self):
        return self.name

class Product(models.Model):
    product_id=models.AutoField(primary_key=True)
    product_name=models.CharField(max_length=100)
    category=models.CharField(max_length=100,default="")
    subcategory=models.CharField(max_length=50,default="")
    price=models.IntegerField(default=0)
    desc=models.CharField(max_length=300)
    image=models.ImageField(upload_to='shop/images',default="")



    def __str__(self):
        return self.product_name



class Cart(models.Model):
    products=models.CharField(max_length=5000)
    myuser=models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.myuser.email + "cart"


class Orders(models.Model):
    myuser=models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=50,default="")
    email=models.CharField(max_length=50,default="")
    address=models.CharField(max_length=500,default="")
    phoneno=models.IntegerField(default=0)
    price=models.IntegerField(default=0)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    qty=models.IntegerField(default=1)
    razorpay_pid=models.CharField(max_length=500,default="NULL")
    razorpay_oid=models.CharField(max_length=500,default="NULL")
    razorpay_sign=models.CharField(max_length=500,default="NULL")
    ispaid=models.CharField(max_length=500,default="Pending")

    def __str__(self):
        return self.myuser.email+"orders"

    

