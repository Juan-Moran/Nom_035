from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def entrada(request):

    return render(request, 'entrada.html')