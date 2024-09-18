
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm,  ClearableFileInput
from Cuestionarios.models import Trabajador, Empresa
from .models import Archivo

class CustomUserCreationForm( UserCreationForm):
    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'email', 'username', 'password1', 'password2']
        
class EmpresaForm( ModelForm):
    class Meta:
        model = Empresa
        fields = '__all__'
        exclude= ['delEmpresario']

#--------------------------------------Para iniciar con los datos del trabajador por parte del patrón
class CustomTrabajadorForm( ModelForm):
    class Meta:
        model = Trabajador
        fields = ["nombre", "tPuesto", "tContrato", "tPersonal", "tJornada", "rotacion", "eLaboral"]

#-------------------------------------Para que el trabajador complete su info
class CustomEmpleadoForm( ModelForm):
    class Meta:
        model  =  Trabajador
        fields = ["nombre", "genero", "edad", "nEstudios", "eTerminados", "experiencia"]  

class FormBusca(forms.Form):
    cadena = forms.CharField()
    cadena.widget.attrs.update({'class':'form-control', 
                                'placeholder':'Nombre o parte del nombre del empleado'})
    cadena.widget.attrs.update(size = 100)

class CustomClearableFileInput(ClearableFileInput):
    template_with_clear = '<br>  <label for="%(clear_checkbox_id)s">%(clear_checkbox_label)s</label> %(clear)s'

class FormArchivo(ModelForm):
    class Meta:
        model = Archivo
        fields = '__all__'
        widgets = {
            'archivo': CustomClearableFileInput
        }
class FormPreguntaSioNo(forms.Form):
    OPCIONES =[
        ('1',"Si"),
        ('2',"No"),
    ]
    like = forms.ChoiceField(
        widget=forms.RadioSelect, choices=OPCIONES,
    )

class FormPreguntaLikert(forms.Form):
    OPCIONES =[
        ('1',""),
        ('2',""),
        ('3',""),
        ('4',""),
        ('5',""),
    ]
    like = forms.ChoiceField(
        widget=forms.RadioSelect, choices=OPCIONES,
    )
