from django.shortcuts import render,redirect
from django.contrib import messages
from eapp.models import Contact,Product,Cart,Orders
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.conf import settings
import razorpay
from django.http import HttpResponse
# Create your views here.
def index(request):
    prods={}
    for cat in Product.objects.raw('Select * from eapp_product order by(category)'):
        #print(cat.product_id)
        #print(cat.category)
        if cat.category in prods:
            prods[cat.category].append(cat)
        else:
            prods[cat.category]=[cat]
    cartitems=0
    if request.user.is_authenticated:
        try:
            carti=Cart.objects.get(myuser=request.user)
        except:
            carti=Cart(myuser=request.user,products="*,")
            carti.save()
        cartitems=carti.products.split(',')  #  *,=[*," "]
        if(len(cartitems)>1):
            cartitems=cartitems[0:len(cartitems)-1]
        print("My items in cart are")
        print(cartitems)
        
    #print(prods)
    params={
        'prods': prods,
        'cartitems': cartitems,
    }
    return render(request,"index.html",params)

def contact(request):
    if request.method=="POST":
        name=request.POST['name']
        email=request.POST['email']
        desc=request.POST['desc']
        pnumber=request.POST['pnumber']
        mycontacts=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        mycontacts.save()
        messages.success(request,"We'll get back to you soon")
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")


def addCart(request,pid):
    if request.user.is_authenticated:
        messages.success(request,f"Added Item {pid} to cart")
        try:
            carti=Cart.objects.get(myuser=request.user)
            carti.products=carti.products+str(pid)+","
            carti.save()
            obj=Product.objects.get(product_id=pid)
            print(obj)
        
        except Exception as e:
            print(e)
        return redirect('/cart')
    return redirect('/auth/login')

def viewproduct(request,pid):
    
    try:    
        prod=Product.objects.get(product_id=pid)
        v=1
    except:
        prod="Not found"
        v=0
    print(v)
    cartitems=['*',]
    if request.user.is_authenticated:
        cart=Cart.objects.get(myuser=request.user)
        cartitems=cart.products.split(',')
    cartitems=cartitems[0:len(cartitems)-1]
    #print(len(cartitems))
    params={
        'prod':prod,
        'v':v,
        'cartitems': cartitems,

    }
    return render(request,"view.html",params)

def delCart(request,pid):
    if request.user.is_authenticated:
        cart=Cart.objects.get(myuser=request.user)
        cartitems=cart.products.split(',')
        cartitems=cartitems[0:len(cartitems)-1]
        if pid in cartitems:
            cartitems.remove(pid)
            messages.success(request,f"Successfully deleted {pid} from cart")
            temp=""
            for i in cartitems:
                temp+=str(i)+','
            cart.products=temp
            cart.save()
        else:
            messages.warning(request,f"Item {pid} not in Cart")
        #print(cartitems)
        return redirect('/cart')
    return redirect('/auth/login')


def cart(request):
    cart=Cart.objects.get(myuser=request.user)
    cartitems=cart.products.split(',')
    cartitems=cartitems[0:len(cartitems)-1]
    cartitems.remove('*')
    cartdict={}
    totalprice=0
    for items in cartitems:
        try:
            cartobj=Product.objects.get(product_id=items)
        #we can do out of stock option here
            if cartobj in cartdict:
                cartdict[cartobj]+=1
                totalprice+=cartobj.price
            else:
                cartdict[cartobj]=1
                totalprice+=cartobj.price
        except:
            pass
    print(totalprice)
    print(cartdict)
    params={
        'cartdict':cartdict,
        'cartitems':cartitems,
        'totalprice':totalprice
    }
    return render(request,'cart.html',params)

def checkout(request):
    if request.method=='POST':
        cart=Cart.objects.get(myuser=request.user)
        cartitems=cart.products.split(",")
        cartitems=cartitems[0:len(cartitems)-1]
        cartitems.remove('*')
        cartdict={}
        totalprice=0
        for items in cartitems:
                try:
                    cartobj=Product.objects.get(product_id=items)
        #we can do out of stock option here
                    if cartobj in cartdict:
                        cartdict[cartobj]+=1
                        totalprice+=cartobj.price
                    else:
                        cartdict[cartobj]=1
                        totalprice+=cartobj.price
                except:
                    pass
        print("Post hello")
        client=razorpay.Client(auth=(settings.KEY,settings.SECRET))
        payment=client.order.create({'amount':(totalprice*100), 'currency':'INR', 'payment_capture':1})
        name=request.POST['name']
        email=request.POST['email']
        address=request.POST['address']
        pnumber=request.POST['pnumber']
        for key,val in cartdict.items():
            ord=Orders(name=name,email=email,address=address,phoneno=pnumber,myuser=request.user,product=key,qty=val,price=(val*(key.price)),razorpay_oid=payment['id'])
            ord.save()
        
        print(payment)
        params={
            'payment':payment
        }
        return render(request,"blank.html",params)
    
    cart=Cart.objects.get(myuser=request.user)
    cartitems=cart.products.split(",")
    cartitems=cartitems[0:len(cartitems)-1]
    cartitems.remove('*')
    cartdict={}
    totalprice=0
    for items in cartitems:
        try:
            cartobj=Product.objects.get(product_id=items)
        #we can do out of stock option here
            if cartobj in cartdict:
                cartdict[cartobj]+=1
                totalprice+=cartobj.price
            else:
                cartdict[cartobj]=1
                totalprice+=cartobj.price
        except:
            pass
    print(totalprice)
    print(cartdict)

    params={
        'totalprice':totalprice,
          
          'cart':cart
    }

    return render(request,'checkout.html',params)

def success(request,pid,oid,sgn):
    data={}
    data['razorpay_order_id']=oid
    data['razorpay_payment_id']=pid
    data['razorpay_signature']=sgn
    client=razorpay.Client(auth=(settings.KEY,settings.SECRET))
    try:
        check=client.utility.verify_payment_signature(data)
        print('*************')
        print(check)
        print('*************')
        orders=Orders.objects.filter(razorpay_oid=oid)
        for order in orders:
            order.razorpay_pid=pid
            order.razorpay_sign=sgn
            order.ispaid="Paid-Yet To be delivered"
            order.save()
        messages.success(request,"Order placed successfully")
        cart=Cart.objects.get(myuser=request.user)
        cart.products="*,"
        cart.save()
        return redirect('/')
    except Exception as e:
        print(e)
        return HttpResponse("Payment cannot be verified")

def failed(request,oid):
    try:
        orders=Orders.objects.filter(razorpay_oid=oid)
        orders.delete()
        return redirect('/cart')
    except:
        return HttpResponse("Error 404")

def orders(request):
    myorders=Orders.objects.filter(myuser=request.user)
    print(myorders)
    v=0
    if len(myorders)==0:
        v=1
    params={
        'orders':myorders,
        'v':v,
    }
    return render(request,'order.html',params)

def cancelOrder(request,oid):
    if request.method=="POST":
            print(oid)
            quant=request.POST['quant']
            if int(quant) ==0:
                return redirect('/orders')
            order=Orders.objects.get(id=oid)
            corder=Orders(
                myuser=order.myuser,
                name=order.name,
                email=order.email,
                address=order.address,
                phoneno=order.phoneno,
                price=int(quant)*(order.product.price),
                product=order.product,
                qty=int(quant),
                razorpay_pid=order.razorpay_pid,
                razorpay_oid=order.razorpay_oid,
                razorpay_sign=order.razorpay_sign,
                ispaid="Cancelled-Refund Awaited"
            )
            corder.save()
            order.qty=order.qty-int(quant)
            order.save()
            if order.qty==0:
                order.delete()
            return redirect('/orders')
    order=Orders.objects.get(id=oid)
    params={
            'order':order
            }
    return render(request,"cancelorder.html",params)

    