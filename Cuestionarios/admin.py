from django.contrib import admin
from .models import Cuestionario, Preguntas, Control, Empresario
from .models import Empresa, Trabajador, Encuesta, Valores, Categoria
from .models import Dominio, Dimension, Valoracion
# Register your models here.
admin.site.register(Cuestionario)
admin.site.register(Preguntas)
admin.site.register(Control)
admin.site.register(Empresario)
admin.site.register(Empresa)
admin.site.register(Trabajador)
admin.site.register(Encuesta)
admin.site.register(Valores)
admin.site.register(Categoria)
admin.site.register(Dominio)
admin.site.register(Dimension)
admin.site.register(Valoracion)