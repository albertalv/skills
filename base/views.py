from typing import Any
from django import http
from django.http import HttpResponse
from django.http.request import HttpRequest
from django.http.response import HttpResponseBase
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,redirect
from agora_token_builder import RtcTokenBuilder
from django.views import View
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.http import JsonResponse
from .forms import LoginForm
from .forms import CustomUserCreationForm
from .models import Stream
from .models import Estatus
import random
import time 
from .models import UserProfile
import json
from django.contrib.auth.models import User
from .models import Paquetes
from django.http import HttpResponseForbidden
import base64
import http.client
from .models import videos
import boto3
import base64
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from django.shortcuts import HttpResponseRedirect, reverse
from .models import suscripciones
from .models import perfilCategoria
from .models import categorias
from django.shortcuts import get_object_or_404
from .models import tipoDenuncia
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import UserSerializer, ConexionSerializer, CategoriaSerializer, TokenSerializer, PaqueteSerializer
from django.contrib.auth import authenticate, login
from .models import masUsuario
from django.utils.functional import wraps
connected = False
# Create your views here.
def getToken(request):
    appId = "380a5ca3bd4f4cd09bd565211dd8aa02"
    appCertificate = "6f4ecbd86ba6480cab672f0c3f6d86ca"
    channelName = request.GET.get("channel")
    uid = random.randint(0,100)
    expirationTimeInSeconds = 3600 * 24
    currentTimeStamp = time.time()
    privilegeExpiredTs = currentTimeStamp + expirationTimeInSeconds
    role = 1
    Stream.objects.filter(channel=channelName).delete()
    token = RtcTokenBuilder.buildTokenWithUid(appId, appCertificate, channelName, uid, role, privilegeExpiredTs)
    stream_obj = Stream(appId= appId, channel = channelName, token = token, uid=uid)
    stream_obj.save()
    return JsonResponse({"token": token, "uid": uid}, safe=False)

class vista(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        saldo= request.GET.get('tokens', None)
        context = {'tokens': tokens}
        context = {
            'tokens': user_profile.tokens, 
            'saldo': saldo,
        }
        return render(request, 'base/lobby.html', context)
    
  
    
    def put(self, request):
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
            return HttpResponse('Error en la actualización de tokens', status=500)

    


def pruebaUno(request):
    return render(request, 'base/pruebaUno.html')
class contenido(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self,request):
            suscripcion = suscripciones.objects.filter(suscriptor=request.user.username)
            usuarios = User.objects.filter(id__in=[s.user_id for s in suscripcion])
            return render(request, 'base/contenido.html', {'suscripcion' : suscripcion, 'usuarios': usuarios})
        
def pruebaDos(request):
    return render(request, 'base/contenidoDos.html')

class vistaInicio(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self,request):
            estatus = Estatus.objects.all()
            usuarios = User.objects.all()
            cat = perfilCategoria.objects.all()
            cato = categorias.objects.all()
            return render(request, 'base/index.html', {'estatus': estatus,'usuarios': usuarios, 'cat':cat,'cato': cato})
        
        def put(self, request):     
            data = json.loads(request.body)
            channel = data.get('channel')
            estado = data.get('estado')
            Estatus.objects.filter(channel=channel).delete()
            objeto_estatus = Estatus(channel = channel, estado = estado)
            objeto_estatus.save()
            return HttpResponse(status=204)
        
@login_required
def profile(request):
    return render(request,'base/profile.html')
@login_required
def admin_profile(request):
    return render(request, 'base/admin_profile.html')
def exit(request):
    logout(request)
    return redirect('inicio')

class custom_login(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        form = LoginForm()
        return render(request, 'registration/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if user.is_superuser:
                    return redirect('admin_profile')
                else:
                    return redirect('profile')
            else:
                return redirect('login')
        else:
            form = LoginForm()
            return render(request, 'registration/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            categoria = form.cleaned_data['categoria']  # Obtenemos la instancia del modelo categorias
            perfilCategoria.objects.create(user=user, category=categoria)  # Asignamos el objeto categoria directamente

            return redirect('login')  # Redirigir a la página de inicio de sesión
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def myTokens(request):
    user_profile = UserProfile.objects.get(user=request.user)
    tokens = user_profile.tokens
    return render(request,'base/misTokens.html', {'tokens':tokens})
@login_required
def myMoney(request):
    return render(request, 'base/money.html')
@login_required
def buzon(request):
    return render(request, 'base/buzon.html')
@login_required
def validacion(request):
    return render(request, 'base/validacion.html')
@login_required
def resolverDenuncia(request):
    return render(request, 'base/resolverDenuncia.html')

class crearCat(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        cat = categorias.objects.all()
        return render(request, 'base/crudCategorias.html', {'cat': cat})
    
    
    def post (self, request):
            data = request.POST.get("nombreCategoria")
            objeto_categoria = categorias(nombreCategoria=data)
            objeto_categoria.save()
            return redirect('admin_profile')


class eliminarCat(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def post(self, request, categoria_id):
        categoria = get_object_or_404(categorias, pk = categoria_id)
        categoria.delete()
        return redirect('admin_profile')  ## CODIGO CAMBIADO
    
class elegirCat(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        cat = categorias.objects.all()
        return render(request, 'base/eligeCategoria.html', {'cat': cat})

class crearTipoDenuncia(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        denuncias = tipoDenuncia.objects.all()
        return render(request, 'base/crud_denuncias.html', {'denuncias': denuncias})
    
    def post(self, request):
        nombreDenuncia = request.POST.get("nombreDenuncia")
        if nombreDenuncia:
            objeto_denuncia = tipoDenuncia(nombreDenuncia=nombreDenuncia)
            objeto_denuncia.save()
        return redirect('admin_profile')


class eliminarTipoDenuncia(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request, tipoDenuncia_id):
        denuncia = get_object_or_404(tipoDenuncia, pk=tipoDenuncia_id)
        denuncia.delete()
        return redirect('admin_profile')


class editarTipoDenuncia(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        nombreDenuncia = request.POST.get("denunciaEditada")
        idDenuncia = request.POST.get("identificador")
        objeto_denuncia = tipoDenuncia.objects.get(id=idDenuncia)
        print(nombreDenuncia)
        print(idDenuncia)
        objeto_denuncia.nombreDenuncia = nombreDenuncia
        objeto_denuncia.save()
        return redirect('admin_profile')
      
class verAdmin(View):
        @method_decorator(csrf_exempt, login_required)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self, request):
            cat = categorias.objects.all()
            return render(request,'base/verCategoriasAdmin.html', {'cat': cat})    

@login_required
def tokens(request):
    paquetes = Paquetes.objects.all()
    return render(request, 'base/tokens.html', {'paquetes': paquetes})
def nosotros(request):
    return render(request, 'base/nosotros.html')
def categoryas(request):
    return render(request, 'base/categorias.html')

@login_required
def previo(request):
    referrer = request.META.get('HTTP_REFERER', '')
    context = {
            'referrer': referrer,
        }
    return render(request, 'base/previo.html', context)
    
    

def is_valid_referer(request):
    referer = request.META.get('HTTP_REFERER')  # Obtiene el referer de la solicitud

    # Compara el referer con la URL de la ruta "canal/"
    if referer and '/canal/' in referer:
        return True  # El referer es válido, permite el acceso a la vista
    else:
        return False 
    
class room(View):
    @method_decorator(csrf_exempt)
    
    def dispatch(self, request, *args, **kwargs):
        if not is_valid_referer(request):
            return HttpResponseRedirect(reverse('inicio'))  
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, room_name):
        espectador = UserProfile.objects.get(user=request.user)
        tokensEspectador = espectador.tokens
        username = request.GET.get('username', 'Anonymous')
        user = User.objects.get(username__iexact=room_name)
        hostId= user.id
        return render(request, 'base/room.html', {'room_name': room_name, 'username': username, 'user_id' : hostId, 'tokensEspectador': tokensEspectador})
    
  
class vistaCheckout(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self, request, paquete_id):
            paquete = Paquetes.objects.get(id=paquete_id)
            return render(request,'base/checkout.html', {'paquete': paquete})


class vistaExitoso(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self, request, paquete_id):
            paquete = Paquetes.objects.get(id=paquete_id)
            return render(request,'base/checkoutExitoso.html', {'paquete': paquete})

        def put(self, request):
            data = json.loads(request.body)
            tokens = int(data.get('tokens')) 
            tokens = data.get('tokens')
            user_profile = UserProfile.objects.get(user=request.user)
            user_profile.tokens += tokens
            user_profile.save()
            return HttpResponse('Actualización de tokens exitosa')

class subirVideo(View):
        @method_decorator(csrf_exempt)
        def dispatch(self, request, *args, **kwargs):
            return super().dispatch(request, *args, **kwargs)
        def get(self, request):
            videos_del_usuario = videos.objects.filter(user=request.user)
            s3 = boto3.client('s3', 
            aws_access_key_id = 'AKIAUQIPTLA4NKIENKFW',
            aws_secret_access_key = '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')
            bucket_name = 'pruebaskills'
            nombres_videos = [video.videos for video in videos_del_usuario if video.videos]
            
            videos_base64 = []
            for nombre in nombres_videos:
                key = nombre
                response = s3.get_object(Bucket=bucket_name, Key=key)
                video_content = response['Body'].read()
                video_base64 = base64.b64encode(video_content).decode('utf-8')
                videos_base64.append(video_base64)
   
            return render(request,'base/subirVideo.html', {'videos': videos_base64})
        
        def post (self, request):

            try:
                user_profile = videos.objects.get(user=request.user)
            except ObjectDoesNotExist:
                user_profile = videos(user=request.user)

            
            uploaded_file = request.FILES['video_file'] 
            file_name = uploaded_file.name
            # Guarda el archivo subido en el bucket de S3 utilizando Boto3
            s3 = boto3.client('s3', 
            aws_access_key_id = 'AKIAUQIPTLA4NKIENKFW',
            aws_secret_access_key = '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')
            bucket_name = 'pruebaskills'
            s3.upload_fileobj(uploaded_file, bucket_name, file_name)

        
            videos.objects.create(user=request.user, videos=file_name)
                
            return redirect('profile')

def optional_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('login')
    return _wrapped_view

class vistaDePerfil(View):
    @method_decorator(csrf_exempt,login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, room_name):
        mas = masUsuario.objects.get(user_id = request.user.id)
        valu = mas.precioCanal
        cet = perfilCategoria.objects.get(user_id = request.user.id)
        usuario = User.objects.get(id=room_name)
        suscripcion = suscripciones.objects.filter(user_id = room_name, suscriptor= request.user).exists() #NUEVA ACTUALIZACION ##########
        user_profile = UserProfile.objects.get(user=request.user)
        tok = user_profile.tokens
        videos_del_usuario = videos.objects.filter(user=room_name)
        s3 = boto3.client('s3', 
        aws_access_key_id = 'AKIAUQIPTLA4NKIENKFW',
        aws_secret_access_key = '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')
        bucket_name = 'pruebaskills'
        nombres_videos = [video.videos for video in videos_del_usuario if video.videos]
            
        videos_base64 = []
        for nombre in nombres_videos:
            key = nombre
            response = s3.get_object(Bucket=bucket_name, Key=key)
            video_content = response['Body'].read()
            video_base64 = base64.b64encode(video_content).decode('utf-8')
            videos_base64.append(video_base64)
   
        return render(request,'base/vistaPerfil.html', {'videos': videos_base64, 'room_name': room_name, 'tokens': tok, 'usuario': usuario, 'suscripcion':suscripcion, 'valu':valu, 'cet':cet})
    
class vistaDePrueba(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
   
    def put(self, request):
        data = json.loads(request.body)
        tokens = int(data.get('tokens'))
        host_id = data.get('hostId')
        usuario_id = data.get('userId')
        suscriptor = data.get('suscriptor')
        
        host_profile = UserProfile.objects.get(user_id=host_id)
        user_profile = UserProfile.objects.get(user_id=usuario_id)
        host_profile.tokens += tokens
        user_profile.tokens -= tokens
        host_profile.save()
        user_profile.save()
        
        host_suscripciones = suscripciones.objects.get(user_id=host_id)
        host_suscripciones.suscriptor = suscriptor
        host_suscripciones.save()

        return HttpResponse('Actualización de tokens exitosa')
        
"""class vistaSuscripciones(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'base/paraSuscripciones.html')
    
    def put(self, request):
        try:
            data = json.loads(request.body)
            suscriptor = data.get('suscriptor')
            host_id = data.get('hostId')
            host, created = suscripciones.objects.get_or_create(user_id=host_id)
            host.suscriptor = suscriptor
            host.save()

            return HttpResponse('Actualización de suscriptor exitosa')

        except suscripciones.DoesNotExist:
            return HttpResponse('Usuario no encontrado', status=400)

        except Exception as e:
            return HttpResponse('Error en la actualización de suscriptor', status=500)"""

@api_view(['GET'])
def getRoutes(request): 
    routes = [
        {
            'Endpoint': '/authentication/',
            'method': 'GET',
            'body': None,
            'description': 'Endpoint para autentificar', 
        },
        {
            'Endpoint': '/logIn/',
            'method': 'POST',
            'body': None,
            'description': 'Endpoint para entrar', 
        }
    ]
    
    return Response(routes)

@api_view(['GET'])
def getViews(request):
    user = User.objects.all()
    serializer = UserSerializer(user, many = True)
    return Response(serializer.data)

@api_view(['POST'])
def getLogin(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        # Autenticación exitosa
        user_info = {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'id': user.id,
            # Agrega otros campos que desees enviar al frontend
        }

        return Response(user_info)
    else:
        return Response({'error': 'Credenciales inválidas'}, status=400)

@api_view(['POST'])
def getRegister(request):
    form = CustomUserCreationForm(request.data)

    if form.is_valid():
        user = form.save()
        return Response({'message': 'Registro exitoso'})
    else:
        errors = form.errors.as_json()
        return Response({'error': errors}, status=400)

@api_view(['GET'])   
def getConexion(request):
    estatus = Estatus.objects.all()
    serializer = ConexionSerializer(estatus, many = True)
    return Response(serializer.data)

@api_view(['GET'])   
def getCat(request):
    cate = categorias.objects.all()
    serializer = CategoriaSerializer(cate, many = True)
    return Response(serializer.data)

def search_results(request):
    query = request.GET.get('query', '')
    cat = perfilCategoria.objects.all()
    results = User.objects.filter(username__icontains=query).values('id', 'username')
    data = []
    for result in results:
        data.append({
            'id': result['id'],
            'username': result['username'],
        })

    return JsonResponse(data, safe=False)

@api_view(['GET'])
def getCategorias(request):
    categorias = categorias.objects.all()
    serializer = CategoriaSerializer(categorias, many = True)
    return Response(serializer.data)

class obtenerTokens(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
   
    def put(self, request):
        data = json.loads(request.body)
        tokens = int(data.get('tokens'))
        host_id = data.get('hostId')
        
        
        host_profile = UserProfile.objects.get(user_id=host_id)
        host_profile.tokens += tokens
        host_profile.save()

        return HttpResponse('Actualización de tokens exitosa')

@api_view(['GET'])
def getNumeroTokens(request, fk):
    toke = UserProfile.objects.get(user_id = fk)
    serializer = TokenSerializer(toke, many = False)
    return Response(serializer.data)

@api_view(['GET'])
def getPaquetesTokens(request):
    paquetes = Paquetes.objects.all()
    serializer = PaqueteSerializer(paquetes, many = True)
    return Response(serializer.data)

@api_view(['PUT'])
def actualizarTokens(request, fk):
    try:
        # Obtener el usuario correspondiente al ID 'fk' desde la base de datos
        usuario = UserProfile.objects.get(user_id=fk)

        # Obtener la cantidad de tokens enviados en la solicitud POST
        saldo_nuevo = int(request.data['saldo'])

        # Sumar la cantidad de tokens nuevos al saldo existente del usuario
        usuario.tokens += saldo_nuevo
        usuario.save()

        # Devolver una respuesta con un mensaje de éxito
        return Response({'mensaje': f'Saldo actualizado correctamente. Nuevo saldo: {usuario.tokens}'}, status=200)

    except UserProfile.DoesNotExist:
        # Si no se encuentra el usuario, devolver una respuesta de error
        return Response({'mensaje': 'Usuario no encontrado'}, status=404)

    except Exception as e:
        # Si ocurre algún otro error, devolver una respuesta de error
        return Response({'mensaje': f'Error al actualizar el saldo: {str(e)}'}, status=500)

class nuevo(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
   
    def get(self, request):
        cat = perfilCategoria.objects.all()
        cato = categorias.objects.all()
        return render(request, 'base/nuevaCat.html', {'cat':cat,'cato': cato})

class crudDeUsuario(View): 
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        usuario = User.objects.get(id = request.user.id)
        cate = perfilCategoria.objects.get(user = request.user)
        cat = categorias.objects.all()
        mas = masUsuario.objects.get(user_id = request.user.id)
        valu = mas.precioCanal
        return render(request, 'base/crud_user.html', {'usuario': usuario, 'cate': cate, 'cat': cat, 'mas':mas, 'valu': valu})

class paginaPrincipal(View): 
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    def get(self, request):
        return render(request, 'base/paginaPrincipal.html')

class editarNombre(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        nombre = request.POST.get("nombre")
        identificador = request.POST.get("identificador")
        objeto_nombre = User.objects.get(id=identificador)
        objeto_nombre.first_name = nombre
        objeto_nombre.save()
        return redirect('profile')

class editarApellido(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        apellido = request.POST.get("apellido")
        identificador = request.POST.get("identificador")
        objeto_apellido = User.objects.get(id=identificador)
        objeto_apellido.last_name = apellido
        objeto_apellido.save()
        return redirect('profile')

class editarCategoria(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        ca = request.POST.get("categoria")
        identificador = request.POST.get("identificador")
        objeto_categoria = perfilCategoria.objects.get(user_id=identificador)
        objeto_categoria.category= ca
        objeto_categoria.save()
        return redirect('profile')

class administradorCategoria(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        ca = request.POST.get("categoria")
        identificador = request.POST.get("identificador")
        objeto_cat = categorias.objects.get(id=identificador)
        objeto_cat.nombreCategoria = ca
        objeto_cat.save()
        return redirect('admin_profile')

class elegirPrecioCanal(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        precio = request.POST.get("precio")
        identificador = request.POST.get("identificador")
        objeto_precio = masUsuario.objects.get(user_id=identificador)
        objeto_precio.precioCanal = precio
        objeto_precio.save()
        return redirect('profile')

class elegirSexo(View):
    @method_decorator(csrf_exempt, login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def post(self, request):
        sex = request.POST.get("sex")
        identificador = request.POST.get("identificador")
        objeto_sexo = masUsuario.objects.get(user_id=identificador)
        objeto_sexo.sexo = sex
        objeto_sexo.save()
        return redirect('profile')