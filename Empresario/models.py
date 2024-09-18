from django.db import models
from Cuestionarios.models import *
from django.forms import ModelForm, ClearableFileInput
# Create your models here.

class FormEmpresa(ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        exclude = ('delEmpresario','actividad')
#-------------------------- Un modelo para guardar archivos ----------
class Archivo(models.Model):
    archivo = models.FileField(upload_to="media/", null=True, blank=True)        