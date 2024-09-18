from django.db import models
from django import forms
from django.forms import ModelForm, ClearableFileInput

#----------------------------------------------------------
#-         Modelo de Cuestionario    
# para lograr que no se esté repitiendo el nombre de la 
# encuesta y para administrar mejor las preguntas que le 
# corresponden se crea una tabla para almacenar el nombre de
# la encuesta y queda descrita de mediante la siguiente tabla.
#----------------------------------------------------------
class Cuestionario(models.Model):
    nombre = models.CharField(max_length=250)
    nulo = models.SmallIntegerField(default = 0)
    bajo = models.SmallIntegerField(default = 0)
    medio = models.SmallIntegerField(default= 0)
    alto = models.SmallIntegerField(default= 0)
    
    def __str__(self):
        return self.nombre
    def numero(self):
        num = self.nombre.split("-")
        return num[0]
    def desc(self):
       num = self.nombre.split("-")
       return num[1] 

    #-- Sólo se almacena el nombre del cuestionario
#----------------------------------------------------------
#-         Modelo de Preguntas                            
# Se separan las preguntas y almacenan juntas en esta tabla 
# donde se almacenará un número de pregunta, la pregunta o 
# reactivo en si (texto) y el tipo de pregunta para que al 
# desplegar se pueda saber que tipo de respuesta se espera.
#----------------------------------------------------------
class Preguntas(models.Model):
    opciones_tipo =[
        (1, "Likert"),
        (2, "Si o No"),
        (3, "Sección"),
    ]
    num = models.CharField(max_length=2)
    #-- Número de la pregunta según la encuesta de la NOM-035.
    #   Para las preguntas que no tienen numeración usar letras.
    reactivo = models.CharField(max_length=500)
    #-- Pregunta a realizar o sección
    origen = models.ForeignKey(Cuestionario, on_delete=models.CASCADE)
    #-- Si se borra el cuestionario, se borra en cascada las preguntas asociadas.
    tipo = models.SmallIntegerField(choices=opciones_tipo, default =1)
    #-- Si es de tipo likert despliega los 5 valores esperados y espera 
    # respuesta, si es de Si o No despliega las dos opciones y regresa 
    # Verdadero para saltar a otra sección.
    def __str__(self):
        tipo =""
        for tip,tx in self.opciones_tipo:
            if tip == self.tipo:
                tipo = tx
        return f"{self.num}.- {self.reactivo} (tipo: {tipo})"
    def espregunta(self):
        tipo = True
        if  (self.tipo == 3):#--- tipo sección?
            tipo = False
        return tipo
#--------------------------------------------------------------
#-         Modelo de Control                                   
# En el sistema se requiere que los cuestionarios sean        
# controlados en cuanto al despliegue de sus preguntas,       
# asi entonces esta tabla se usa para definir la secuencia    
# de las preguntas y secciones, se debe capturar en una cadena
# de números o letras separadas por una coma.                 
#--------------------------------------------------------------
class Control(models.Model):
    controlde =models.ForeignKey(Cuestionario,on_delete = models.CASCADE)
    secuencia = models.TextField(max_length=300,blank=True, unique= False, )
    def __str__(self):
        return f"{self.controlde} se pregunta con la secuencia :{self.secuencia}"
    def verificar(self):
        preguntas=[]
        reactivos = Preguntas.objects.filter(origen = self.controlde)
        preguntas = self.secuencia.split(",")
        bandera = True
        for cada_uno in preguntas:
            bandera = bandera and (reactivos.filter( num = cada_uno).count()==1)

        return bandera
#--------------------------------------------------------------
#-         Modelo de Empresario                                   
# Se requiere que un empresario genere el espacio para las 
# empresas a las que realizará la aplicación de la NOM-035 
# para lo cual se requiere una autorización en el sistema 
# mediante su contraseña.
#--------------------------------------------------------------
class Empresario(models.Model):
    nombre = models.CharField(max_length=50, unique= False)
    apellido = models.CharField(max_length=50, unique=False, default=" ")
    usuario = models.CharField(max_length=12, blank= False, unique= True, default="usuario")
    def __str__(self):
        return f"{self.nombre.strip()} {self.apellido.strip()}/{self.usuario.strip()}"
    def nempresas(self):
        negocios = Empresa.objects.filter( delEmpresario = self).count()
        return negocios

#--------------------------------------------------------------
#-         Modelo de Empresa                                   
# Colección de datos relevantes para ser usados en los reportes 
# visuales o documentos que se generen de la aplicación de las 
# encuestas, para ello se revisa la norma oficial NOM-035 y se 
# observa los datos de nombre o razón social, domicilio y 
# actividad, para lo cual se ha revisado los códigos que usa 
# el INEGI para identificar las actividades en el pais y para 
# este proyecto de investigación se ha determinado dejar fijo 
# como 7221 que corresponde a “Servicios de preparación de 
# alimentos y bebidas”.
#--------------------------------------------------------------
class Empresa(models.Model):    
    opcEstado =[
        ("Ags", "Aguascalientes"),
        ("Bc", "Baja California"),
        ("Bcs", "Baja California Sur"),
        ("Cam","Campeche"),
        ("Chi","Chiapas"),
        ("Chh","Chihuahua"),
        ("Cdm","Ciudad de México"),
        ("Coa","Coahuila"),
        ("Col","Colima"),
        ("Dur","Durango"), 
        ("Edm","Estado de México"),
        ("Gua","Guanajuato"),
        ("Gue","Guerrero"),
        ("Hid","Hidalgo"),
        ("Jal", "Jalisco"),
        ("Mic","Michoacán"),
        ("Mor","Morelos"),
        ("Nay", "Nayarit"),
        ("Nl","Nuevo León"),
        ("Oax", "Oaxaca"),
        ("Pue","Puebla"),
        ("Que","Querétaro"),
        ("Qro","Quintana Roo"),
        ("SLP","San Luis Potosí"),
        ("Sin","Sinaloa"),
        ("Son","Sonora"),
        ("Tab","Tabasco"),
        ("Tam","Tamaulipas"),
        ("Tla","Tlaxcala"),
        ("Ver","Veracruz"),
        ("Yuc","Yucatán"),
        ("Zac", "Zacatecas")
    ]

    delEmpresario = models.ForeignKey(Empresario, on_delete=models.CASCADE)
    razonSocial = models.CharField(max_length=100, blank=False, unique=False)
    #domicilio = models.CharField(max_length=500)
    calle = models.CharField(max_length=30, blank= True)
    numero = models.SmallIntegerField(default = 1)
    interior = models.CharField(max_length=15, blank= True)
    colonia = models.CharField(max_length=25, blank= True)
    codigoPostal = models.CharField(max_length=5, blank= True)
    población = models.CharField(max_length=20, blank= True)
    municipio = models.CharField(max_length=20, blank= True)
    estado = models.CharField(max_length=3, choices=opcEstado, default="Jal")
    # Debe poder descomponerse en calle, num exterior, num interiror, colonia, C. P., ciudad, estado
    actividad = models.CharField(max_length=4, default = "7221")
    def __str__(self):
        return self.razonSocial.strip()
    def domicilio(self):
        cadena = f"{self.calle.strip()} #{self.numero} {self.interior.strip()}, {self.colonia.strip()} C. P. {self.codigoPostal} "
        if self.población == self.municipio:
            cadena = cadena+f"{self.municipio.strip()}, {self.estado.strip()}."
        else:
            cadena = cadena+f"{self.población.strip()}, {self.municipio.strip()}, {self.estado.strip()}."
        return cadena
    def Edo(self):
        cadena = self.opcEstado[self.estado]
        return cadena
    def nombre_corto(self):
        return self.razonSocial[0:4]
#--------------------------------------------------------------
#-         Modelo de Trabajador
# Datos del trabajador según la NOM-035 como: su nombre, género, 
# edad, nivel de estudios terminados/inconclusos, tipo de puesto, 
# tipo de contrato, tipo de personal (sindicalizado, confianza o 
# ninguno), tipo de jornada, rotación de turnos, experiencia en 
# el puesto, experiencia laboral. Los datos son recopilados en 
# dos partes, el trabajador captura primero y el empresario 
# completa, los campos de los cuales es responsabilidad del 
# empresario son: Tipo puesto, Tipo contrato, tipo Personal, 
# tipo jornada, Rotación y Experiencia en el puesto.                       
#--------------------------------------------------------------
class Trabajador(models.Model):
    opciones_genero = [
        ("M","Masculino"),
        ("F","Femenino"),
    ]
    opciones_edad = [
        ("1", "15 a 19"),
        ("2", "20 a 24"),
        ("3", "25 a 29"),
        ("4", "30 a 34"),
        ("5", "35 a 39" ),
        ("6", "40 a 44"),
        ("7", "45 a 49"),
        ("8", "50 a 54"),
        ("9", "55 a 59"),
        ("A", "60 a 64"),
        ("B", "65 a 69"),
        ("C", "70 o más"),
    ]
    opc_nivel_estudios =[
        ("1", "Primaria"),
        ("2", "Secundaria"),
        ("3", "Bachillerato o Preparatoria"),
        ("4", "Técnico Superior"),
        ("5", "Licenciatura"),
        ("6", "Maestría"),
        ("7", "Doctorado"),
    ]
    opc_estudios_terminados=[
        ("T", "Terminados"),
        ("I", "Inconclusos"),
    ]
    opc_puesto =[
        ("O", "Operativo"),
        ("S", "Supervisor"),
        ("P", "Profesional o técnico"),
        ("G","Gerente"),
    ]
    opc_tipo_contrato =[
        ("O", "Por Obra o proyecto"),
        ("I", "Tiempo indeterminado"),
        ("T","Tiempo determinado o Temporal"),
        ("H","Honorarios"),
    ]
    opc_tipo_personal =[
        ("S", "Sindicalizado"),
        ("C", "Confianza"),
        ("N", "Ninguno"),
    ]
    opc_tipo_jornada=[
        ("D", "Fijo diurno (entre las 6:00 y 20:00 hrs)"),
        ("N", "Fijo nocturno (entre las 20:00 y 6:00 hrs)"),
        ("M", "Fijo mixto (combinación de nocturno y diurno)")
    ]
    opc_experiencia = [
        ("1", "Menos de 6 meses"),
        ("2", "Entre 6 meses y 1 año"),
        ("3", "Entre 1 a 4 años"), 
        ("4", "Entre 5 a 9 años"),
        ("5", "Entre 10 a 14 años"),
        ("6", "Entre 15 a 19 años"),
        ("7", "Entre 20 a 24 años"),
        ("8", "25 años o más"),
    ]
    trabajaEn = models.ForeignKey(Empresa, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=70)
    # Nombre y apellidos del trabajador
    genero = models.CharField(max_length=1, choices=opciones_genero)
    edad = models.CharField(max_length=1, choices=opciones_edad, default="2")
    nEstudios=models.CharField(max_length=1, choices=opc_nivel_estudios, default="1", verbose_name="Nivel de estudios")
    eTerminados = models.CharField(max_length=1, choices=opc_estudios_terminados, default="I", verbose_name="Estudios terminados")
    tPuesto = models.CharField(max_length=1, choices=opc_puesto, default="o", verbose_name="Tipo de puesto")
    tContrato= models.CharField(max_length=1, choices=opc_tipo_contrato, default="I", verbose_name="Tipo de contrato")
    tPersonal= models.CharField(max_length=1, choices=opc_tipo_personal, default="N", verbose_name="Tipo de personal")
    tJornada = models.CharField(max_length=1, choices=opc_tipo_jornada, default="D", verbose_name="Tipo de jornada")
    rotacion = models.BooleanField( )
    experiencia = models.CharField(max_length=1, choices=opc_experiencia, default="3")
    eLaboral= models.CharField(max_length=1, choices=opc_experiencia, default="3", verbose_name="Experiencia laboral")
    def supuesto(self):
       for clve, puesto in self.opc_puesto:
            if clve == self.tPuesto:
                return puesto
         
    def __str__(self):
        cadena = self.nombre+" es "+ self.supuesto()
        return cadena
    def ultimo_cuestionario(self):
        cuestionarios = Cuestionario.objects.all()
        ult_cuestionario = 0
        for cuestionario in cuestionarios:
            encuesta = Encuesta.objects.filter( delCuestionario = cuestionario).get( delTrabajador = self)
            if encuesta.seccion != 99: 
                ult_cuestionario = cuestionario.pk
                break
        return ult_cuestionario
#--------------------------------------------------------------
#-         Modelo de Encuesta                                   
# Para almacenar lo que cada trabajador respondió a las preguntas 
# del cuestionario se le concoce en el sistema como encuesta y 
# consta de una serie de identificadores del cuestionario al que 
# responde y el trabajador que proporcionó las respuestas, las 
# respuestas se recomienda almacenar en una cadena de caracteres 
# en donde cada espacio en ella sea una respuesta a cada pregunta 
# almacenando números de 1 a 5 para las respuestas de tipo likert 
# y una S o una N para las respuestas de SI o NO.
#--------------------------------------------------------------
class Encuesta(models.Model):
    delTrabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    numEncuesta = models.SmallIntegerField()
    # Sin repetir uno por empleado.
    respuestas = models.CharField(max_length=100)
    seccion = models.SmallIntegerField(default = 0)
    # Un carácter por respuesta si no ha contestado en alguna pregunta 
    # se almacena un espacio en blanco.
    delCuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE, null=True)
    califFinal = models.IntegerField( default = 0 )
    
#--------------------------------------------------------------
#-         Modelo de Valores                                   
# Se recomienda realizar funciones dentro de la clase Encuesta que 
# combine con esta tabla y pueda calcular el valor asignado a la 
# respuesta para poder realizar los cálculos que se mencionan en 
# la NOM-035
#--------------------------------------------------------------
class Valores(models.Model):
    delCuestionario =models.ForeignKey(Cuestionario, on_delete=models.CASCADE)
    normales = models.CharField(max_length=200)
    # Cada par de números separados por comas a manera de lista corresponde 
    # al número con el que se identifica a cada pregunta en el cuestionario
    alReves = models.CharField(max_length=200)
    # Funciona igual que el campo anterior, solo verificar que no tengan el 
    # mismo número en ambos campos
    def __str__(self):
        try:
            cadena = f"{str(self.delCuestionario)[:3]} 0-4: {self.normales}/ 4-0: {self.alReves}"
        except:
            cadena = "Vacío"
        return cadena
#--------------------------------------------------------------
#-         Modelo de Categoría
# se requiere hacer referencia a la tabla del cuestionario al 
# que se relaciona, así como el texto con el que se reconoce a 
# dicha categoría.                                
#--------------------------------------------------------------
class Categoria(models.Model):
    delCuestionario = models.ForeignKey(Cuestionario, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, unique = False)
    nulo = models.SmallIntegerField(default = 0)
    bajo = models.SmallIntegerField(default = 0)
    medio = models.SmallIntegerField(default= 0)
    alto = models.SmallIntegerField(default= 0)
    
    def __str__(self):
        try:
            cadena = f"{str(self.delCuestionario)[:3]} -> {self.descripcion}"
        except:
            cadena = "Vacío"
        return cadena
#--------------------------------------------------------------
#-         Modelo de Dominio
# para ubicar los nombres de cada dominio y se relacionan a una 
# categoría en específico.
#--------------------------------------------------------------
class Dominio(models.Model):
    deCategoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, unique= False)
    nulo = models.SmallIntegerField(default = 0)
    bajo = models.SmallIntegerField(default = 0)
    medio = models.SmallIntegerField(default= 0)
    alto = models.SmallIntegerField(default= 0)
    
    def __str__(self):
        return f"{str(self.deCategoria)[:3]} -> {self.descripcion}"

#--------------------------------------------------------------
#-         Modelo de Dimensión
# Aparte de tener la procedencia de su dominio, también tiene el 
# texto que lo identifica y los números de las respuestas que la 
# conforman. Nota: debe hacerse la suma de los valores obtenidos 
# de cada una de las respuestas asociadas.
#--------------------------------------------------------------
class Dimension(models.Model):
    deDominio = models.ForeignKey(Dominio, on_delete=models.CASCADE)
    descripcion = models.CharField(max_length=200, unique= False)
    # Texto que define a la dimensión
    reactivos = models.CharField(max_length=100, unique=False)
    # Pares de números, separados por coma para indicar el número 
    # del reactivo del cuestionario

    def __str__(self):
        return f"{self.deDominio}-->{self.descripcion}=> {self.reactivos}"
#--------------------------------------------------------------
#-         Modelo de Valoración
# Se observa que la valoración de una categoría es la suma de 
# la valoración de uno o varios dominios y cada valor de dominio 
# tiene uno o varias dimensiones, cada valor de dimensión tiene 
# asociada una o varias respuestas del cuestionario.
#--------------------------------------------------------------
class Valoracion(models.Model):
    deEncuesta = models.ForeignKey(Encuesta, on_delete=models.CASCADE)
    # para saber a cual grupo de respuestas del trabajador corresponde
    deDimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    # para saber de que dimensión es el valor
    valor = models.IntegerField()
    # Aquí se pone la suma de los reactivos interpretados de la encuesta

########################################################################
#################### Foratos de captura.
class FormBusca( forms.Form ):
    cadena = forms.CharField()
    
    cadena.widget.attrs.update({'class':'form-control', 
                                    'placeholder':'Nombre del cuestionario'})
    cadena.widget.attrs.update(size = 200)

class Formlista(forms.Form):
    nombre_cuestionario = forms.CharField( max_length=100)
    numero_reactivos = forms.CharField( max_length=4)
    control = forms.CharField( max_length=7)

class FormPregunta(ModelForm):
    class Meta:
        model = Preguntas
        fields = '__all__'
#####################################

