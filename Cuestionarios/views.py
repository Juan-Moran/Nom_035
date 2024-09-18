from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.http import Http404

from Cuestionarios.models import Cuestionario, Preguntas, Control, Empresario
from Cuestionarios.models import Empresa, Trabajador, Encuesta, Valores
from Cuestionarios.models import Categoria, Dimension, Dominio, Valoracion
from Cuestionarios.models import Formlista, FormPregunta

# Create your views here.
#################################################
#  INDEX : lista los cuestionarios capturados   #
#################################################
def index(request):
    cuest = Cuestionario.objects.all()
    renglon =[]
    controlador = False
    for objeto in cuest:
        reactivos = Preguntas.objects.filter(origen=objeto)
        controlador = Control.objects.filter(controlde =objeto)
        if controlador.count() >0:
            controla = controlador[0]
            controlador = controla.verificar()
        #-------------

        renglon.append( (objeto.nombre, f"{reactivos.count()}", controlador ))
    
    context = {
            "renglon": renglon 
        }
    return render( request, "Cuestionarios/cuestionarios.html", context)
####################################################################
#  REACTIVOS : lista los reactivos de un cuestionario capturados   #
####################################################################
def reactivos(request, id):
    try:
        cuestionario = Cuestionario.objects.get(pk= id)
    except Cuestionario.DoesNotExist:
        raise Http404("El cuestionario no existe")
    lista = Preguntas.objects.filter( origen = cuestionario)
    contexto = {"nombre": cuestionario.nombre,
                "lista" : lista
                } 
    return render(request, "Cuestionarios/reactivos.html", contexto)
"""  
####################################################################
#  EDITAR : edita un reactivo de un cuestionario capturados      #
####################################################################
def editar(request, id):
    pregunta = Preguntas.objects.get(id=id)
    if request.method == 'GET':
        forma = FormPregunta( instance = pregunta )
    else:
        forma = FormPregunta( request.POST, instance = pregunta )
        if forma.is_valid():
            forma.save()
            
            return HttpResponseRedirect(reverse('reactivos'))
    
    return render(request, "Cuestionarios/edita.html", {'forma':forma})

"""