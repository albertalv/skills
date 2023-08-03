from django.contrib import admin

# Register your models here.
from .models import Paquetes, videos, categorias

admin.site.register(Paquetes)
admin.site.register(videos)
admin.site.register(categorias)