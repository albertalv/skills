from django.shortcuts import render
from base.models import UserProfile
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View

import json
def previo(request):
    return render(request, 'chat/previo.html')

"""def room(request, room_name):
    username = request.GET.get('username', 'Anonymous')
    user = User.objects.get(username__iexact=room_name)
    host_id= user.id

    return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'user_id' : host_id})"""

"""class room(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self, request, room_name):
        espectador = UserProfile.objects.get(user=request.user)
        tokensEspectador = espectador.tokens
        username = request.GET.get('username', 'Anonymous')
        user = User.objects.get(username__iexact=room_name)
        hostId= user.id
        return render(request, 'chat/room.html', {'room_name': room_name, 'username': username, 'user_id' : hostId, 'tokensEspectador': tokensEspectador})
    
    def put(self, request, room_name):
        data = json.loads(request.body)
        tokens = int(data.get('tokens'))
        host_id = data.get('hostId')
        
        try:
            user_profile = UserProfile.objects.get(user=request.user)
            host_profile = UserProfile.objects.get(user_id=host_id)
            
            if tokens > user_profile.tokens:
                return HttpResponse('No tienes suficientes tokens', status=400)
            
            user_profile.tokens -= tokens
            host_profile.tokens += tokens
            user_profile.save()
            host_profile.save()
            
            return HttpResponse('Actualización de tokens exitosa')
        
        except UserProfile.DoesNotExist:
            return HttpResponse('Usuario no encontrado', status=400)
        
        except Exception as e:
            return HttpResponse('Error en la actualización de tokens', status=500)"""
    
  
        
    