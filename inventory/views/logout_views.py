from django.contrib.auth import logout
from django.shortcuts import redirect

def custom_logout(request):
    request.session.flush()   #clears session
    logout(request)
    return redirect('login')