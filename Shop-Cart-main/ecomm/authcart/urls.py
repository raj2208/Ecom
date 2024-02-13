from django.urls import path,include
from authcart import views
urlpatterns = [
    path('signup/',views.signup,name="signup"),
    path('login/',views.handleLogin,name="handleLogin"),
    path('logout/',views.handleLogout,name="handleLogout"),
    path('authenticate/<email>/<token>',views.handleAuthenticate,name="handleAuthenticate"),
    
]
