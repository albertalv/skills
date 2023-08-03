from rest_framework.serializers import ModelSerializer

from .models import User, Estatus, categorias, UserProfile, Paquetes

class UserSerializer(ModelSerializer): 
    class Meta: 
        model = User
        fields = '__all__'
class ConexionSerializer(ModelSerializer): 
    class Meta: 
        model = Estatus
        fields = '__all__'
class CategoriaSerializer(ModelSerializer):
    class Meta: 
        model = categorias
        fields = '__all__'
class TokenSerializer(ModelSerializer):
    class Meta: 
        model = UserProfile
        fields = '__all__'
class PaqueteSerializer(ModelSerializer):
    class Meta: 
        model = Paquetes
        fields = '__all__'
