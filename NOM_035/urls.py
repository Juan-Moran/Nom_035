"""
URL configuration for NOM_035 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from Cuestionarios.views import *
from Empresario.views import *


urlpatterns = [
    path('admin/', admin.site.urls, name = "admin"),
    path('Cuestionarios', index),
    path('Cuestionarios/<id>', reactivos, name="reactivos"),
    ##path('Cuestionarios/edita/<id>', editar),
    path('Empresarios/', lista_empresarios, name='empresarios'),
    path('nuevoEmpresario/', regEmpresario, name='registra'),
    path('Empresario/edita/<id>', edita_Empresario, name='edita_empresario'),
    path('Empresario/<patron>', ver_empresas, name='ver_empresas'),
    path('Empresario/crea/<patron>', crea_empresa, name='crea_empresa'),
    path('Empresario/edita/empresa/<int:negocio>',edita_empresa, name="edita_empresa"),
    path('Empresario/empresa/lista/<id>', empleados, name='lista_empleados'),
    path('Empresario/empleados/<id>',agrega,name='ag_empleados' ), # varios xlsx
    path('Empresario/empleado/<id>',crea_empleado, name="nuevoEmpleado"), # uno
    path('Empresario/empleado/edita/<id>', edit_empleado, name ='editEmpleado'),
    path('Empresario/empleado/borrar/<id>',elimina_trabajador, name='borra_trabajador'),
    path('encuesta/',encuesta, name="encuesta"),
    path('requiere/<id>',requiere_atención, name = "atencion"),
    path('califica/<int:cuestionarioID>/<int:trabajadorID>',calificacion, name="califica"),
    path('',entrada, name='entrada'),
    path('conclusion/<int:empresaID>', conclusion, name='conclusion'),
    path('export/<int:empresa>/<int:id>',exportar,name='exportar'),
    path('export/<int:empresa>',exportar, name='exportar1'),
    path('logout/', exit, name="exit"),
    path('login/',login,name="login"),
    path('accounts/', include('django.contrib.auth.urls')),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#Omar jklmn03-hj