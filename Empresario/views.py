from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import Http404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import *
from django.contrib.auth.models import User, Group, Permission
from django.urls import reverse
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import logout, login, authenticate
from django.contrib import messages
from django.conf import settings
from .forms import CustomUserCreationForm, CustomTrabajadorForm, FormBusca, FormArchivo, CustomEmpleadoForm, EmpresaForm
import django_excel as Excel
from datetime import datetime



# Create your views here.
#######################################################################
#   Envia_correo : 
#  Aquí se envía un mensaje por correo electrónico con uno o varios 
# nombres de usuario y su contraseña.
######################################################################
def envia_correo(request, mensaje, cuantos):
    tema = "Cuentas de Trabajadores creadas"
    renglon = []
    msg = ""
    if cuantos !=1:
        for ren in mensaje:
            msg = f"<tr><td>{ren[0]}</td><td>{ren[1]}</td><td>{ren[2]}</td><td>{ren[3]}</td></tr>"
            renglon.append(msg)
        datos = {
            'name': "Sistema-Nom-035",
            'email':"No-responder@nom035.com",
            'subject':tema,
            'datos':renglon
            }
        template = render_to_string('email-template.html', datos)
    else:
        msg = f"{mensaje[0]} <Br> nombre de usuario:{mensaje[2]} <Br> contraseña:{mensaje[3]}" 
        msg = f"Se agregó un trabajador a {mensaje[1]}\n <br>"+msg
        datos = {
            'name': "Sistema-Nom-035",
            'email':"No-responder@nom035.com",
            'subject':tema,
            'datos':msg
            } 
        template = render_to_string('email-template-uno.html', datos)
    
    emailSender = EmailMessage(
        tema, template, settings.EMAIL_HOST_USER,
        ['juan.ma@bahia.tecnm.mx']
    )
    emailSender.content_subtype = 'html'
    emailSender.fail_silently = False
    emailSender.send()

    messages.success(request, 'Se envió un correo con los usuarios y contraseñas al administrador')
    return 

#######################################################################
#   Permisos_empresario: 
#  Recolecta los permisos de un usuario y regresa si puede o no ver una 
# empresa.
######################################################################
def permisos_empresario(usuario):
    puede = False
    permisos = usuario.get_all_permissions()
    puede = 'Cuestionarios.view_empresa' in permisos
    return puede


#######################################################################
#   Ver_empresas : 
#  Recolecta las empresas creadas por un empresario y las muestra en 
# una lista.
######################################################################
@login_required
def ver_empresas(request, patron):
    dueño = Empresario.objects.get(id= patron)
    puede = permisos_empresario(request.user)
    esadmin = request.user.is_staff
    if puede:
        empresas = Empresa.objects.filter(delEmpresario = dueño)
        encuestas = []
        for emp in empresas:
            encuestados = Trabajador.objects.filter( trabajaEn = emp).count()
            terminaron = 0
            for t in Trabajador.objects.filter( trabajaEn = emp):
                respondio = Encuesta.objects.filter(delTrabajador = t)
                for r in respondio:
                    if r.seccion == 99:
                        terminaron +=1 
            reportar = f"{encuestados*3}/{terminaron}"
            encuestas.append( [emp.razonSocial, emp.domicilio, reportar,emp.id] )

        datos ={
            'empresa':encuestas,
            'patron':dueño,
            'menu':esadmin
        }
    else:
        msg = "Tu sesión como Empresario no existe."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)
    return render(request, "Empresario/empresas.html",datos)

#######################################################################
#   Crea_empresa : 
#  Un empresario logueado puede crear empresas en el sistema para 
# posteriormente agregarle empleados y que ellos contesten las encuestas
######################################################################
@login_required
def crea_empresa(request, patron):
    dueño = Empresario.objects.get( id = patron)
    puede = permisos_empresario( request.user)
    if puede:
        if request.method == 'POST':
            forma = FormEmpresa( request.POST )
            if forma.is_valid():
                nueva_Empresa = forma.save( commit=False )
                nueva_Empresa.delEmpresario = dueño
                nueva_Empresa.save()
                rutaEmpresas = '/Empresario/'+str(dueño.id) 
                return HttpResponseRedirect( rutaEmpresas )
        else:
            forma = FormEmpresa()
        contexto = {
            'forma':forma,
            'patron':dueño
        }
    else:
        msg = "Tu sesión no es válida como Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)

    return render(request,"Empresario/add_empresa.html",contexto )
#######################################################################
#   Crea_empleado : 
#  Un empresario logueado puede agregar empleados de uno por uno a cada
# empresa que haya creado, esta función es para llamar el html que lo 
# agrega a la lista de empleados. Cada trabajador deberá contar con 
# nombre de usuario y una contraseña.
######################################################################
@login_required
def crea_empleado(request, id):
    puede = permisos_empresario( request.user)
    if puede:
        empresa = Empresa.objects.get( id = id)
        msg = ''
        permisos = []
        permiso = Permission.objects.get(codename='add_encuesta' )
        permisos.append(permiso)
        permiso = Permission.objects.get(codename='change_encuesta')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_preguntas') 
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='change_trabajador')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_encuesta')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_trabajador')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_cuestionario')
        permisos.append(permiso)
        respuesta = "."
        if request.method == 'POST':
            if request.POST["cancel"]:
                return redirect( "lista_empleado")
            else:
                nuevoTrabajador = CustomTrabajadorForm( request.POST )
                if nuevoTrabajador.is_valid():
                    empleadoNuevo = nuevoTrabajador.save(commit = False)
                    usuario = User()
                    usuario.first_name = nuevoTrabajador.cleaned_data["nombre"]
                    empleadoNuevo.trabajaEn = empresa
                    empleadoNuevo.save()
                    #--------------------- se guardó el trabajador, ahora su usuario en el sistema
                    nombre_usuario = empresa.nombre_corto()+str(empleadoNuevo.pk)
                    usuario.username =nombre_usuario
                    pass_usuario = "Nom-035$"+str(empleadoNuevo.pk)
                    usuario.set_password(pass_usuario)
                    usuario.save()
                    envia_correo( request, mensaje=[nuevoTrabajador.cleaned_data["nombre"],empresa.razonSocial,usuario.username,pass_usuario],cuantos=1)
                    #-------------------- se guardó el usuario, ahora a generar sus respuestas
                    cuestionarios = Cuestionario.objects.all()
                    for cuestionario in cuestionarios:
                        respuestas = Encuesta()
                        respuestas.respuestas = respuesta
                        respuestas.delCuestionario = cuestionario
                        respuestas.delTrabajador = empleadoNuevo
                        respuestas.seccion =0
                        respuestas.numEncuesta = empleadoNuevo.pk
                        respuestas.save()
                    #-------------------- se guardó las respuestas, ahora poner permisos.
                    for perm in permisos:
                        usuario.user_permissions.add( perm )
                    usuario.save()
                    msg=f'¡Trabajador {empleadoNuevo} agregado correctamente!'
                    nuevoTrabajador= CustomTrabajadorForm
        else:
            nuevoTrabajador = CustomTrabajadorForm
        datos = {
            'forma': nuevoTrabajador,
            'empresa':empresa,
            'mensaje': msg
        }
    else:
        msg = "Tu sesión no es válida como Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)

    return render( request, "Empresario/empleado.html", datos )
#######################################################################
#   Edit_empleado : 
#  Un empresario logueado puede editar los datos de los  empleados de una
# empresa que haya creado, esta función es para editar datos de empleados. 
# Aquí no se puede cambiar la contraseña.
######################################################################
@login_required
def edit_empleado(request, id):
    puede = permisos_empresario( request.user)
    if puede:
        empleado = Trabajador.objects.get( pk = id)    

        if request.method == 'GET':
            forma = CustomTrabajadorForm( instance = empleado)
        else:
            forma = CustomTrabajadorForm( request.POST, instance = empleado )
            if forma.is_valid():
                forma.save()
            return redirect( 'lista_empleados', empleado.trabajaEn.pk)
    else:
        msg = "Tu sesión no es válida como Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)

    return render( request, 'Empresario/edita.html', {'forma':forma, 'empleado':empleado})

#######################################################################
#   entrada : 
#  Todos los usuarios entran aquí, se loguean y luego se les acomoda el
# menú según su tipo de usuario.
######################################################################
def entrada(request):
    permisos = request.user.get_all_permissions()
    usuario =""
    extra = ""
    #detectar si es administrador del sistema 
    if request.user.is_staff:
        menu = 1
        usuario = request.user.first_name
    elif "Cuestionarios.add_empresa" in permisos:
        menu = 2
        usuario = request.user.first_name
        empresario_id = Empresario.objects.get( usuario = request.user.username ).pk
        extra = empresario_id
        #detecta si es un Empresario
    elif "Cuestionarios.change_encuesta" in permisos:
        #declaramos el menu para Trabajadores
        menu = 3
        usuario = request.user.first_name
        extra = Trabajador.objects.get( nombre = request.user.first_name).trabajaEn.pk
    else:
        menu = 0
        usuario = "Visitante"

    datos={
        'menu':menu,
        'usuario':usuario,
        'extra': extra
    }
    """
    else: #menú para el que no se ha logueado
        datos ={
            'menu': '<i class="fa-solid fa-door-open" style="color: #4d22b3;"></i>'
        }
    """
    return render(request, "entrada.html",datos)
    

#######################################################################
#   regEmpresario : 
#  Sólo para un administrador del sistema, genera empresarios nuevos en
# el sistema, es importante que guarde la contraseña puesta aquí.
######################################################################
@login_required
def regEmpresario( request ):
    permiso = request.user.is_staff
    if permiso:
        if request.method == 'POST':
            user_creation_form = CustomUserCreationForm(data=request.POST)
            if user_creation_form.is_valid():
                user_creation_form.save()
                usuario = User.objects.get(username=user_creation_form.cleaned_data["username"])
                grupoEmpresarios = Group.objects.get(name = 'Empresario')
                usuario.groups.add(grupoEmpresarios) 
                empresario = Empresario()
                empresario.usuario = user_creation_form.cleaned_data["username"]
                empresario.nombre =user_creation_form.cleaned_data["first_name"]
                empresario.apellido = user_creation_form.cleaned_data["last_name"] 
                empresario.save()
                return redirect('entrada')
        else:
            user_creation_form = CustomUserCreationForm()
            
        data ={
            'form': user_creation_form
        }
    else:
        msg = "Tu sesión no es válida como Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)

    return render(request, 'registration/register.html', data)
#######################################################################
#   Empresarios: 
#  Sólo para un administrador del sistema, lista los empresarios que están 
#  registrados en el sistema, permite crear un nuevo empresario y editar 
#  o borrar a los que están ya registrados.
######################################################################
@login_required
def lista_empresarios(request):
    permiso = request.user.is_staff
    if permiso:
        empresarios = Empresario.objects.all()

        datos = {
            'Ente': empresarios
        }
    else:
        msg = "Tu sesión no es válida, solo para Administradores del sistema."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto) 
    return render(request, 'empresarios.html', datos )

#######################################################################
#   Edita_empresarios: 
#  Sólo para un administrador del sistema, edita los datos de un 
#  empresario, incluye el password.
######################################################################
@login_required
def edita_Empresario(request, id):
    permisos = request.user.is_staff()
    if permisos:
        empresario = Empresario.objects.get( pk = id)
        usuario = User.objects.get( username = empresario.usuario)

        if request.method == 'GET':
            forma = CustomUserCreationForm( instance = usuario)
        else:
            forma = CustomUserCreationForm( request.POST, instance = usuario )

            if forma.is_valid():
                forma.save()
                return redirect( 'lista_empresarios')
            
        datos = {
            'forma': forma,
            'empresario':empresario
        }
    else:
        msg = "Tu sesión no es válida, solo para Administradores del sistema."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto)         
    return render(request, 'Empresario/editar.html', datos )
#######################################################################
#   exit : 
#  Es una forma de salir del sistema 
#
######################################################################
def exit(request):
    logout(request)
    return redirect('entrada')

#######################################################################
#   empleados : 
#  Esté método es para listar empleados que se han registrado en una empresa
# 
######################################################################
@login_required
def empleados(request, id):
    permisos = permisos_empresario(request.user)
    if permisos:
        empresa = Empresa.objects.get( pk = id)
        empleados = Trabajador.objects.filter( trabajaEn = empresa )
        c1 = Cuestionario.objects.get( pk = 1)
        c2 = Cuestionario.objects.get( pk = 2)
        c3 = Cuestionario.objects.get( pk = 3)

        resultado = empleados
        if request.method == 'POST':
            busqueda = FormBusca( request.POST )
            if busqueda.is_valid():
                busca = busqueda['cadena'].value()
                R =[]
                for emp in empleados:
                    if busca in emp.nombre:
                        R.insert( 0, emp)
                resultado = R
        else:
            busqueda = FormBusca()
            resultado =empleados
            for emp in empleados:
                requiere_atención(emp.pk) 
        contesto = Encuesta.objects.all()

        datos = {
            #'form':CustomTrabajadorForm,
            'empresa':empresa,
            'empleados': resultado,
            'formulario':busqueda,
            'respuestas':contesto,
            'C1':c1, 'C2':c2, 'C3':c3
        }
    else:
        msg = "Tu sesión no es válida, se requiere usuario y contraseña de Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto) 

    return render( request, 'Empresario/listado.html', datos)
#######################################################################
#   Elimina : 
#  Aquí se elimina un trabajador de la lista, debe haberse verificado
# antes de proceder.
######################################################################
def elimina_trabajador(request, id):
    try:
        instancia = Trabajador.objects.get( pk = id)
    except Trabajador.DoesNotExist:
        msg = "El trabajador no existe, no se puede eliminar"
        raise Http404(msg)
    empresa = instancia.trabajaEn.pk
    instancia.delete()
    
    return redirect(  'lista_empleados', empresa, permanent= True)


#######################################################################
#   agrega : 
#  Aquí se prepara para la lectura de un archivo en excel con los datos
# de trabajadores de una empresa. Esta opción es solo para Empresarios
######################################################################
def handle_uploaded_file(f):
    narchivo ='Empleados.xlsx'
    with open(narchivo, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
########################################### se requiere para importar xls
@login_required
def agrega(request, id):
    puede = permisos_empresario(request.user)
    if puede:
        todo_bien = True
        permisos = []
        permiso = Permission.objects.get(codename='add_encuesta' )
        permisos.append(permiso)
        permiso = Permission.objects.get(codename='change_encuesta')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_preguntas') 
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='change_trabajador')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_encuesta')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_trabajador')
        permisos.append(permiso)
        permiso= Permission.objects.get( codename='view_cuestionario')
        permisos.append(permiso)
        empresa = Empresa()
        respuestas = "."
        try:
            empresa = Empresa.objects.get(pk = id)
        except Empresa.DoesNotExist:
            todo_bien = False
            msg = "Revise, la empresa a la que quiere agregar los empleados no existe." 

        if request.method == 'POST':
            form = FormArchivo( request.POST, request.FILES )
            if form.is_valid():
                handle_uploaded_file( request.FILES['archivo'] ) 
                muchosEmpleados = pan.read_excel('Empleados.xlsx')
                msg = ""
                try:
                    empresa = Empresa.objects.get(pk = id)
                except Empresa.DoesNotExist:
                    todo_bien = False
                    msg = "Revise, la empresa a la que quiere agregar los empleados no existe."
                datos_usuarios = []
                #-------------- sacar los datos del archivo
                for n in range(0, len(muchosEmpleados)):
                    usuario_pendiente = ""
                    nombre    = muchosEmpleados[n:n+1]['Nombre'][n]
                    tpuesto   = muchosEmpleados[n:n+1]['tipo_Puesto'][n]
                    tContrato = muchosEmpleados[n:n+1]['Tipo_Contrato'][n]
                    tPersonal = muchosEmpleados[n:n+1]['tipo_personal'][n]
                    tJornada  = muchosEmpleados[n:n+1]['tipo_jornada'][n]
                    rotacion  = muchosEmpleados[n:n+1]['rotación'][n]=="Si"
                    eLaboral  = muchosEmpleados[n:n+1]['experiencia_laboral'][n] 
                    trabajador = Trabajador()
                
                    if todo_bien:
                        trabajador.nombre    = nombre
                        trabajador.tPuesto   = tpuesto[0]
                        trabajador.tContrato = tContrato[0]
                        trabajador.tPersonal = tPersonal[0]
                        trabajador.tJornada  = tJornada[0]
                        trabajador.rotacion  = rotacion
                        trabajador.eLaboral  = eLaboral[0]
                        trabajador.trabajaEn = empresa
                        trabajador.save()
                        #----------------------- se guardó el trabajador, ahora el usuario
                        Tusuario = User()
                        Tusuario.first_name = trabajador.nombre
                        nombre_usuario = empresa.nombre_corto()+str(trabajador.pk)
                        Tusuario.username = nombre_usuario
                        Tusuario.password = "Nom-035$"+str(trabajador.pk)
                        Tusuario.save()
                        #guardar para enviar un correo}
                        usuario_pendiente = [trabajador.nombre,empresa,nombre_usuario,Tusuario.password]
                        datos_usuarios.append( usuario_pendiente)
                        respuesta = "."
                        #-------------------- se guardó el usuario, ahora a generar sus respuestas
                        cuestionarios = Cuestionario.objects.all()
                        for cuestionario in cuestionarios:
                            respuestas = Encuesta()
                            respuestas.respuestas = respuesta
                            respuestas.delCuestionario = cuestionario   
                            respuestas.delTrabajador = trabajador
                            respuestas.seccion =0
                            respuestas.numEncuesta = trabajador.pk
                            respuestas.save()
                #-------------------- se guardó las respuestas, ahora poner permisos.
                        for perm in permisos:
                            Tusuario.user_permissions.add( perm )
                        Tusuario.save() 
                if todo_bien:
                    envia_correo(request,datos_usuarios,len(datos_usuarios))
                    return HttpResponseRedirect( '/Empresario/empresa/lista/'+str(empresa.pk))
            else:
                msg = "revisa los datos que capturaste"
                messages.error(request, msg)
                contexto = {
                    'messages': messages
                }
            return render(request, 'entrada.html', contexto)
        else:
            form = FormArchivo()
        return render(request, 'Empresario/alta_empleados.html', {'form': form, 'empresa':empresa })
    else:
        msg = "Tu sesión no es válida, se requiere usuario y contraseña de Empresario."
        messages.error(request, msg) 
        contexto = {
                    'message': messages
                }
        return render(request, 'entrada.html', contexto) 


def pagina(request,id):
    
    return True

#######################################################################
#   Encuesta : 
#  Aquí se presenta las preguntas de los cuestionarios para ser contestados
# por los trabajadores de cada empresa.
######################################################################
@login_required
def encuesta(request):
    class seccion():
        textoSeccion =""#--- si es un salto aquí se pone SALTO
        tipoSeccion  =0 #--- 1 para si o no, 2 para Likert y 3 para Salto
        n_preguntas  =0 #--- si es un salto aquí se pone el índice de llegada o 99 para fin
        preguntas    = []
        pos_preguntas = 0
        def __str__(self):
            if self.tipoSeccion ==1:
                tipo = "Likert"
            elif self.tipoSeccion ==2:
                tipo = "Si o No"
            else: 
                tipo = "SALTO"
            return self.textoSeccion +" "+tipo+"->"+str(self.n_preguntas)
        def __init__(self):
            self.preguntas=[]
            self.n_preguntas=0
            self.tipoSeccion=0
            self.textoSeccion = ""
            return None
        #----------------------------------------- extrae las secciones de un control de cuestionario
    def extrae_secciones(cuestionario, control):
        sec_cuestionario = []
        seccion_nueva = seccion()
        seccion_nueva.textoSeccion =""
        seccion_nueva.preguntas =[]
        pos_cuestion = 0

        for npreg in control:
            #--------------------------------------------- es un salto ?
            if "@" in npreg: #-- se encontró un salto
                seccion_nueva.n_preguntas = len(seccion_nueva.preguntas)
                sec_cuestionario.append(seccion_nueva)
                #------- se guarda la sección previa al salto
                
                seccion_nueva = seccion()#--- nueva sección para el salto
                
                seccion_nueva.textoSeccion = "SALTO"
                seccion_nueva.tipoSeccion = 3
                seccion_nueva.preguntas =[]
                if npreg[1:]=="FIN":
                    seccion_nueva.n_preguntas = 99
                else:
                    seccion_nueva.n_preguntas = len(sec_cuestionario)+1
                sec_cuestionario.append(seccion_nueva)
                #-------------------------------------- guardamos el salto
                
                seccion_nueva = seccion()#--- nueva sección
                seccion_nueva.textoSeccion =""
                seccion_nueva.preguntas =[]
                
                #------------------------ guardamos la sección de salto
            else:
                reactivo = cuestionario.get( num = npreg )
            #----------------------------------------------- Es pregunta?
                if reactivo.espregunta():
                    seccion_nueva.preguntas.append(reactivo.reactivo)
                    pos_cuestion +=1
                    if seccion_nueva.tipoSeccion == 0:
                        seccion_nueva.tipoSeccion = reactivo.tipo
                else:#------------------------------------------- Es Sección?
                    if seccion_nueva.textoSeccion =="":
                        seccion_nueva.textoSeccion = reactivo.reactivo
                        #pos_cuestion +=1
                        seccion_nueva.pos_preguntas = pos_cuestion
                        
                    
                    else:#---------------------- ya tenia una sección
                        seccion_nueva.n_preguntas = len(seccion_nueva.preguntas)
                        sec_cuestionario.append(seccion_nueva)
                        
                        #--- calculamos el número de preguntas y guardamos la sección
                        seccion_nueva = seccion()#--- Nueva sección
                        #pos_cuestion +=1
                        seccion_nueva.pos_preguntas = pos_cuestion
                        seccion_nueva.textoSeccion = reactivo.reactivo
                        seccion_nueva.preguntas = []
                    
        seccion_nueva.n_preguntas = len(seccion_nueva.preguntas)
        sec_cuestionario.append(seccion_nueva)
     
        return sec_cuestionario
    #--------------------------------- Generador de <form> en html -------------------------------
    def crea_paginas( secciones ):
        paginas = []
        for secc in secciones:
            html = ""
            if secc.tipoSeccion ==1:#--Es tipo Likert
                html +=f'<br><h3>{secc.textoSeccion}</h3><br><table class ="table table-primary"><tr><th width=100 class="table table-dark" >Pregunta</th><th width= 50 class="table table-dark">Siempre</th><th width= 50 class="table table-dark">Casi siempre</th><th width= 50 class="table table-dark">Algunas veces</th><th width= 50 class="table table-dark">Casi nunca</th><th width= 50 class="table table-dark">Nunca</th></tr>'
                for n in range(0,secc.n_preguntas):
                    html +=f'<tr><td ><p>{secc.pos_preguntas+n+1}.- {secc.preguntas[n]}</p></td><td width=40 ><p><input required type="radio" id="p{secc.pos_preguntas+n}lk1" name="pregunta_{secc.pos_preguntas+n}" value="1"><label for="p{secc.pos_preguntas+n}lk"></label></p></td><td width=40 ><p ><input required type="radio" id="p{secc.pos_preguntas+n}lk2" name="pregunta_{secc.pos_preguntas+n}" value="2"><label for="p{secc.pos_preguntas+n}lk2"></label></p></td><td width=40 ><p ><input required type="radio" id="p{secc.pos_preguntas+n}lk3" name="pregunta_{secc.pos_preguntas+n}" value="3"><label for="p{secc.pos_preguntas+n}lk3"></label></p></td><td width=40 ><p ><input required type="radio" id="p{secc.pos_preguntas+n}lk4" name="pregunta_{secc.pos_preguntas+n}" value="4"><label for="p{secc.pos_preguntas+n}lk4"></label></p></td><td width=40 ><p ><input required type="radio" id="p{secc.pos_preguntas+n}lk5" name="pregunta_{secc.pos_preguntas+n}" value="5"><label for="p{secc.pos_preguntas+n}lk5"></label></p> </td></tr>'

            elif secc.tipoSeccion == 2:#-- Es de tipo Si o No
                html = f'<table class = "table table-primary"><tr><th width=150 ><h5>Pregunta o Secci&oacuten </h5></th><th width= 60>Si </th><th width= 60>No </th></tr><tr ><td colspan=3 ><p >{secc.textoSeccion}</p></td></tr>'
                for n  in range(0,secc.n_preguntas):
                    html += f'<tr><td ><p>{secc.preguntas[n]}</p></td><td width=60 ><p><input required type="radio" id="p{secc.pos_preguntas+n}si" name="pregunta_{secc.pos_preguntas+n}" value="S"><label for="p{secc.pos_preguntas+n}si">Si</label><br></p></td><td width=60><p><input type="radio" id="p{secc.pos_preguntas+n}no" name="pregunta_{secc.pos_preguntas+n}" value="N"><label for="p{secc.pos_preguntas+n}no">No</label><br></p></td></tr>'
            elif secc.tipoSeccion == 3:#-- Es un salto
                if secc.n_preguntas == 99:
                    html = f'Salto:FIN'
                else:
                    html = f'Salto:{secc.n_preguntas+1}:'
            html += '</table>'
            paginas.append(html)
        return paginas
    #---------------------- Esta función es para desplegar el cuestionario 1
    def obten_html(respuestas):
        #recuperar las preguntas del cuestionario
        cuestionario = respuestas.delCuestionario
        controla = Control.objects.get( controlde = cuestionario )
        controlReactivos = controla.secuencia.split(",")
        preguntas = Preguntas.objects.filter( origen = cuestionario )
        secciones =extrae_secciones(preguntas, controlReactivos)
        #--- cada sección es una página
        pagina_html = crea_paginas(secciones)
        return pagina_html
    
    #----------------------------------------------------------------------------------------------
    #------------------------------ Aquí empieza --------------------------------------------------
    #---------------------------------------------------------------------------------------------- 
    trabaja = request.user.first_name
    vaacontinuar = False
    
    #------------Primero termina de cargar su información.
    if request.method == 'GET':
        try:
            empleado = Trabajador.objects.get( nombre = trabaja )
        except Trabajador.DoesNotExist:
            msg = "Tu sesión como trabajador no existe."
            messages.error(request, msg)
            contexto = {
                'message': messages
            }
            return render(request, 'entrada.html', contexto) 
        datosFaltantes = CustomEmpleadoForm( instance = empleado )
        
        enviar = {
            "faltantes":datosFaltantes
        }
    else:#--   Fue un POST -------------------------------------------------
        empleado = Trabajador.objects.get( nombre = trabaja)
        if 'nombre' in request.POST:
            datosFaltantes = CustomEmpleadoForm( request.POST )
            if datosFaltantes.is_valid():
                empleado.nombre      = datosFaltantes.cleaned_data["nombre"]
                empleado.edad        = datosFaltantes.cleaned_data["edad"]
                empleado.genero      = datosFaltantes.cleaned_data["genero"]
                empleado.edad        = datosFaltantes.cleaned_data["edad"]
                empleado.nEstudios   = datosFaltantes.cleaned_data["nEstudios"]
                empleado.eTerminados = datosFaltantes.cleaned_data["eTerminados"]
                empleado.experiencia = datosFaltantes.cleaned_data["experiencia"]
                empleado.save()
                
                #verificar si ya terminó de contestar la encuesta si no, que termine
                verifica =  empleado.ultimo_cuestionario()
                if verifica != 0:
                    cuestiona = Cuestionario.objects.get( pk = verifica)
                    enc = Encuesta.objects.filter(delTrabajador = empleado ).get( delCuestionario =cuestiona)
                    
                    #............Segundo debe contestar el cuestionario
                    Html = obten_html(enc); #--- contestarlo
                    n_pag = enc.seccion
                    valido = True
                    while valido:
                        if n_pag >= len(Html):
                            enc.seccion = 99
                            enc.save() 
                            cuestiona = Cuestionario.objects.get( pk = empleado.ultimo_cuestionario())
                            enc = Encuesta.objects.filter(delTrabajador = empleado ).get( delCuestionario =cuestiona)
                            Html = obten_html(enc); #--- contestarlo
                            n_pag = enc.seccion
                        else:
                            valido = False 
                        
                    contexto ={
                            'forma': Html[n_pag],
                            'pagina':n_pag,
                            'encuesta': cuestiona.nombre
                            }
                else:
                    messages.success(request,"¡Ya ha concluido las encuestas!")
                    contexto ={
                            'message':messages
                            }  
                    return render(request, 'entrada.html', contexto)              
        else:
            try:
                empleado = Trabajador.objects.get( nombre = trabaja )
            except Trabajador.DoesNotExist:
                msg = "Tu sesión como trabajador no existe."
                messages.error(request, msg)
                contexto = {
                    'message': messages
                }
                return render(request, 'entrada.html', contexto)
            
            cuestiona = Cuestionario.objects.get( pk = empleado.ultimo_cuestionario())
            respuestas = Encuesta.objects.filter( delTrabajador = empleado).get( delCuestionario = cuestiona)
            n_pag = respuestas.seccion+1
            #--------------------------------- recuperar las respuestas y guardar
            resp = respuestas.respuestas
            if len(resp.strip())<100:
                resp.ljust(100-len(resp)," ")

            
            for var in request.POST: #-------- obtiene lo que se contestó
                val = str(request.POST[var])
                p = var.split('_')
                if p[0] == 'pregunta':
                    pos = int(p[1])
                    resp = resp[:pos] + val + resp[pos+1:]
                    vaacontinuar = val=='S' or vaacontinuar
            respuestas.respuestas = resp
            
            respuestas.seccion +=1 #--- seccion siguiente
            respuestas.save()
            #-------------------------------------------------------------------
            enc = Encuesta.objects.filter(delTrabajador = empleado ).get( delCuestionario =cuestiona)
            
            #............Segundo debe contestar las demás secciones del cuestionario
            Html = obten_html(enc); #--- contestarlo
            if enc.seccion < len(Html):
        
                #---------------- control de saltos ----------------------------------------
                if ("Salto" in Html[enc.seccion] ):
                    if not vaacontinuar:
                        adonde = Html[respuestas.seccion].split(":")
                        if  "FIN" in adonde[1]:
                            enc.seccion = 99
                            enc.save()
                            return redirect( 'entrada')#-- regresa a la entrada. 
                        
                        else:
                            n_pag = int( adonde[1] )
                            enc.seccion = n_pag
                            enc.save()
                    else:
                        vaacontinuar = False
                        n_pag = enc.seccion+1
                        enc.seccion +=1
                        enc.save()
                #-----------------------------------------------------------------------------
            if len(Html) > n_pag:
                contexto ={
                    'forma': Html[n_pag],
                    'pagina':n_pag,
                    'encuesta': cuestiona.nombre
                    }
            else:
                enc.seccion = 99
                enc.save()
                return redirect( 'entrada')#-- regresa a la entrada.
                
        return render(request,'preguntas.html', contexto )
        #return redirect( 'entrada')#-- regresa a la entrada.  
    
    return render( request, 'encuesta.html', enviar )

#########################################################################
#   Requiere_atención:                                                  #
#     Determina si el trabajador requerirá atención clínica, requiere   #
#  que el trabajador haya contestado la encuesta 01                     #
#  Las condiciones son:                                                 #
#     a) haber respondido si a alguna pregunta de sección II            #
#     b) haber respondido si a tres o más preguntas de sección III      #
#     c) haber respondido si a dos o más preguntas de sección IV        #
#  Esta función regresa una lista de trabajadores y su valoración       #
#########################################################################
def requiere_atención(id):
    
    cuestionario = Cuestionario.objects.get(pk = 1)#--- ojo este número es del cuestionario 1 de la norma
    trabajador = Trabajador.objects.get( pk = id )
    
    enc = Encuesta.objects.filter( delTrabajador=trabajador).get(delCuestionario = cuestionario)
    resp = enc.respuestas
    tamaño = len(resp)
    if tamaño >7:
        hospital_I = resp[7] == "S" or resp[8] == 'S'
    else:
        hospital_I = False
    if tamaño >9:
        secc3 = resp[9:15]
        cuenta = 0
        for r in secc3:
            if r == "S": cuenta +=1
        hospital_II = cuenta >=3
        secc4 = resp[16:20]
        cuenta = 0
        for r in secc4:
            if r == "S": cuenta +=1 
        hospital_III = cuenta >= 2
    else:
        hospital_II = False
        hospital_III = False
    
    
    atención = hospital_I or hospital_II or hospital_III
    if atención:
        enc.califFinal = 100
    else:
        enc.califFinal = 0
    enc.save()

    return enc.califFinal

#########################################################################
#   Calificación:                                                       #
#     Determina la calificación final de un cuestionario, calculando    #
#  primero categoría, dominio y dimensión entre las respuestas dadas    #
#  requiere de el cuestionario y el trabajador                          #
#########################################################################
def calificacion(request, cuestionarioID, trabajadorID):
    #-------------------------------------------------------------------
    def estaEn(num, secuencia):                     #                   |
        siEstá = False                              #                   |
        enArreglo = secuencia.split(",")            #                   |
        for n in range(0,len(enArreglo)):           #                   |
            if int(num) == int(enArreglo[n]):       #                   |
                siEstá = True                       #                   |
        return siEstá                               #                   |
    #-------------------------------------------------------------------
    #------------- Aqui ponemos las cadenas para la página web
    resultado =[]
    #---------------------------------------------------------
    cuestionario = Cuestionario.objects.get(pk= cuestionarioID)
    trabajador = Trabajador.objects.get(pk = trabajadorID)
    empresaId = trabajador.trabajaEn.pk
    encuestado = Encuesta.objects.filter(delCuestionario = cuestionario).get(delTrabajador = trabajador)
    con = Control.objects.get( controlde = cuestionario)

    secuencia = con.secuencia.split(",") #--- orden de las preguntas
    secuencia_limpia = []
    for sec in secuencia:#------------ eliminar los saltos y secciones de la secuencia.        
        if str(sec).isnumeric():
            secuencia_limpia.append(sec)
    
    #------------------------- Se inicia con las categorías que es el nivel más alto
    catego = Categoria.objects.filter( delCuestionario = cuestionario)
    #------------ sacamos los valores reales de cada respuesta ---------------------
    valores = Valores.objects.get( delCuestionario = cuestionario)
    normales = valores.normales
    alReves = valores.alReves
    
    respondio = encuestado.respuestas
    #--------------------- Quitamos las respuestas S 
    mientras = respondio.split("S")
    cad = ""
    for sub in mientras:
        cad +=sub
    respondio = cad
    #--------------------- Quitamos las respuestas N
    mientras = respondio.split("N")
    cad = ""
    for sub in mientras:
        cad +=sub
    respondio = cad
    
    cfinal = 0 #----------- Para la calificación final del cuestionario 
    for categoria in catego:#---------- A cada categoría le sacamos su calificación
        resultado.append(f"{categoria.descripcion}")
        dom = Dominio.objects.filter( deCategoria = categoria)
    
        ccategoria = 0 #------------Para la calificación de la categoría
        for dominio in dom:#----------- calcular calificacion de cada dominio
            dim = Dimension.objects.filter( deDominio = dominio)
            resultado.append(f"- {dominio.descripcion}")
            cdominio = 0 #-----------Para la calificación del dominio
            for dimension in dim:#-------- calcular la calificación de la dimensión
                numReactivos = dimension.reactivos.split(",")#--- números de preguntas de la dimensión
                
                cdimension = 0
                
                for n in numReactivos:# para cada reactivo lo buscamos en la secuencia
                #---------------------------------------------------------------------------------
                    for pos in range(0,len(secuencia_limpia)):
                        if n == secuencia_limpia[pos]: #--- tomamos la posición de la respuesta
                            try:
                                responde = respondio[pos]
                            except:
                                responde = " "
                            valor = 0

                            if responde != " ":
                                if estaEn(n,normales):
                                    valor = int(responde)-1
                                else:
                                    if estaEn(n,alReves):
                                        valor = 5-int(responde)
                            cdimension +=valor
                #-------------------------------------------
                try:#----- si no existe creará uno nuevo -----------------------------------------------------------
                    nuevaValoracion = Valoracion.objects.filter(deDimension = dimension).get(deEncuesta = respuestas) # type: ignore
                except:
                    nuevaValoracion = Valoracion()
                    nuevaValoracion.deDimension = dimension
                    nuevaValoracion.deEncuesta = encuestado
                nuevaValoracion.valor = cdimension
                nuevaValoracion.save()
                cdominio +=cdimension   
                resultado.append( f"--- {dimension.descripcion} = {cdimension}.")
                #---------------------------------------------------------------------------------------------------
            ccategoria += cdominio
            evalua = ""
            if cdominio < dominio.nulo:
                evalua = "-nulo-"
            elif cdominio < dominio.bajo:
                evalua = "-bajo-"
            elif cdominio < dominio.medio:
                evalua = "=Medio="
            elif cdominio < dominio.alto:
                evalua = "*ALTO*"
            else:
                evalua = "** MUY ALTO **"
            resultado.append(f"- Total dominio:{cdominio}"+evalua)

        cfinal += ccategoria
        evalua = ""
        if ccategoria < categoria.nulo:
            evalua = "-nulo-"
        elif ccategoria < categoria.bajo:
            evalua = "-bajo-"
        elif ccategoria < categoria.medio:
            evalua = "=Medio="
        elif ccategoria < categoria.alto:
            evalua = "*ALTO*"
        else:
            evalua = "** MUY ALTO **"
        resultado.append(f"Total categoría:{ccategoria}"+evalua)

        evalua = ""
        if cfinal < cuestionario.nulo:
            evalua = "-nulo-"
        elif cfinal < cuestionario.bajo:
            evalua = "-bajo-"
        elif cfinal < cuestionario.medio:
            evalua = "=Medio="
        elif cfinal < cuestionario.alto:
            evalua = "*ALTO*"
        else:
            evalua = "** MUY ALTO **"
    resultado.append( f"Total encuesta:{cfinal}."+evalua)
    encuestado.califFinal = cfinal
    encuestado.save()
    #--------------------------------------------------------------------------------
    #          Mostrar los resultados 
    resultados = {
        "cuestionario":cuestionario,
        "resultados":resultado,
        "final":cfinal,
        "trabajador": trabajador
    }
    if request.method == 'POST':
        redirect( 'lista_empleados', empresaId )
    return render(request, "resultados.html", resultados)
#########################################################################
#   Edita_empresa:                                                      #
#  Aquí se edita los datos de una empresa, en caso de haber cometido    #
#  un error al crearla                                                  #
#########################################################################
def edita_empresa(request, negocio):
    try:
        empresa = Empresa.objects.get( pk = negocio)
    except:
        messages.error(request,"*-La empresa especificada no existe")
        return redirect( 'entrada')#-- regresa a la entrada.
    
    if request.method == 'POST':
        datos_nuevos = EmpresaForm(request.POST, instance = empresa)
        if datos_nuevos.is_valid():
            datos_nuevos.save()
            dueño = empresa.delEmpresario.pk
            return redirect ( 'ver_empresas', dueño )
    else:
        editar = EmpresaForm( instance=empresa )
        nombre = empresa.razonSocial
        dueño = empresa.delEmpresario.pk

        contexto = {
            'empresa': editar,
            'nombre': nombre,
            'id':negocio,
            'patron':dueño
        }
    return render(request,"Empresario/edit-empresa.html", contexto)

#########################################################################
#   Exportar:                                                           #
#  Aquí se se copian los datos a una hoja de excel que se descarga al   #
#  administrador que la solicita.                                       #
#########################################################################
@login_required
def exportar( request, empresa, id=None ):
    negocio = Empresa.objects.get( pk = empresa )
    if id == None:
        cuestion = Cuestionario.objects.get( pk = 1)
    else:
        cuestion = Cuestionario.objects.get( pk = id )
        try:
            valores = Valores.objects.get( delCuestionario = cuestion)
        except:
            id = None
    print(id)
    preguntas = Preguntas.objects.filter( origen = cuestion )
    
 
    export = []
    #------------------- Agregar los encabezados 
    encabezados = [
        'Encuestado','Genero', 'Edad', 'Nivel de Estudios',
        'Estado de estudios', 'Puesto', 'Contrato', 'Tipo Personal',
        'Jornada','Rotación', 'Experiencia_puesto', 'Experiencia_laboral'
    ]
    controles = Control.objects.get( controlde = cuestion )
    control = controles.secuencia.split(",")
    for preg in control:#--- tomar la lista de preguntas en órden
        if preg[0] !='@':#-- si es salto no usarlo
            pregunta = preguntas.get( num = preg )
            if pregunta.tipo != 3:#--- si es sección no usar
                encabezados.append ( pregunta.reactivo )
    export.append(encabezados)
    #-------------------- Agregar los datos del usuario y sus valoraciones
    encuestada = Encuesta.objects.filter(delCuestionario = cuestion )
    for enc in encuestada:
        renglon=[]
        if enc.delTrabajador.trabajaEn == negocio:
            empleado = enc.delTrabajador
            usuario = User.objects.get( first_name = empleado.nombre)
            renglon.append( usuario.username )
            renglon.append( empleado.genero )
            renglon.append( empleado.edad )
            for x,y in empleado.opc_nivel_estudios:
                if x == empleado.nEstudios:
                    estudios = y
                
            renglon.append( estudios ) 
            renglon.append( empleado.eTerminados )
            renglon.append( empleado.tPuesto )
            renglon.append( empleado.tContrato )
            for x,y in empleado.opc_tipo_personal:
                if x == empleado.tPersonal:
                    indice = y

            renglon.append( indice )
            renglon.append( empleado.tJornada )
            if empleado.rotacion:
                rota = "Si"
            else:
                rota = "No"
            renglon.append( rota )
            renglon.append( empleado.experiencia )
            renglon.append( empleado.eLaboral )
            #--- hasta aquí los datos del empleado sigue lo que respondió

            if id == None:
                for r in enc.respuestas:
                    renglon.append( r )
            else:
                secuencia_limpia = []
                respondio = enc.respuestas
                for sec in control:#------------ eliminar los saltos y secciones de la secuencia.        
                    if str(sec).isnumeric():
                        secuencia_limpia.append(sec)
                    else:
                        if "@" not in sec:
                            duda = preguntas.get( num = sec )
                            if duda.tipo == 2:
                                secuencia_limpia.append(sec)
                #------------------------------------- ver si son de valor inverso

                for pos in range(0,len(secuencia_limpia)):
                    valoresnormales = []
                    for v in valores.normales.split(','):
                        valoresnormales.append(v.strip() )
                    valorescontrarios = []
                    for v in valores.alReves.split(','):
                        valorescontrarios.append( v.strip() )
                    
                    normal = secuencia_limpia[pos] in valoresnormales
                    alreves = secuencia_limpia[pos] in valorescontrarios
                   
                    if pos < len(respondio):
                        if normal:
                            val = int(respondio[pos])-1
                        elif alreves:
                            if respondio[pos] == " ":
                                val = " "
                            else:
                                val = 5-int(respondio[pos])
                        else:#----------------------------- es una respuesta de Si o No
                            val = respondio[pos]
                    else:
                        val =" "
                    renglon.append(val)                          
                
            export.append( renglon )

    today    = datetime.now()
    strToday = today.strftime("%Y%m%d")
    hoja_excel = Excel.pe.Sheet(export)
    nombre_archivo = 'encuesta01'+strToday+".xlsx"
    return Excel.make_response(hoja_excel, "xlsx", file_name=nombre_archivo)

##########################################################################
#   Conclusion:                                                          #
#  Aquí se se expone una página con resultados por empresa y cuestionario#
#  se establecen las ligas de descarga a excel                           #
##########################################################################
def conclusion(request,empresaID):
    empresa = Empresa.objects.get(pk = empresaID)
    cuestionarios = Cuestionario.objects.all()

    datos ={
        'empresa':empresa,
        'cuestionarios':cuestionarios
    }
    
    
    return render(request,'concluye.html',datos)
