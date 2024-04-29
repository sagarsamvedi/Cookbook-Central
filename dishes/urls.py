from django.urls import path
from .views import *


urlpatterns = [
    path('login/',login_page, name= 'login_page'),
    path('logout/',logout_page, name= 'logout_page'),
    path('signup/',signup_page, name= 'signup_page'),
    path('home/',home_page, name= 'home_page'),
    path('update/<int:id>',update, name= 'update'),
    path('delete/<int:id>',delete, name= 'delete'),
    path('add/',add, name= 'add'),
]
