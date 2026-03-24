from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from ..forms.register_form import CustomUserRegisterForm
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.contrib.auth.views import LoginView

class StoreRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_superuser:
            return redirect("admin:index")

        if not request.user.is_authenticated:
            return redirect('login')

        if not request.session.get("store_id"):
            return redirect('select_store')   

        return super().dispatch(request, *args, **kwargs)     

class LandingPageView(TemplateView):
    template_name = "inventory/landing.html"

class CustomLoginView(LoginView):
    template_name = "inventory/login.html"

    def form_valid(self, form):
        messages.success(self.request,"Logged in successfully!")
        return super().form_valid(form)

class RegisterView(CreateView):  
    form_class = CustomUserRegisterForm
    template_name = "inventory/register.html"
    success_url = reverse_lazy('login')  

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request,"Account created successfully! Please Login.")
        return response