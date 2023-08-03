from django.urls import path

from . import views
urlpatterns = [
    path('', views.previo, name='canal'),
    
]