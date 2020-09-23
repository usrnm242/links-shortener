from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('shorten', views.make_new_link, name='make_new_link'),
    path('<str:hash>', views.redirect, name='redirect'),
]
