
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView

from apps.forms import AuthForm
from apps.models import User, District, Region, Category, Product


class AuthView(FormView):
    form_class = AuthForm
    template_name = 'apps/auth/auth.html'
    success_url = reverse_lazy('profile')

    # def get_context_data(self, **kwargs):
    #     data = super().get_context_data(**kwargs)
    #     data['regions'] = Region.objects.all()
    #     return data

    def form_valid(self, form):
        data = form.cleaned_data
        phone_number = data.get("phone_number")
        password = form.data.get("password")
        hash_password = data.get("password")
        query_set = User.objects.filter(phone_number=phone_number)
        if query_set.exists():
            user = query_set.first()
            if user.check_password(password):
                login(self.request, user)
            else:
                messages.error(self.request, "Parol xato !")
                return redirect('login')
        else:
            user = User.objects.create(password=hash_password, phone_number=phone_number)
            login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "\n".join([error[0] for error in form.errors.values()]))
        return super().form_invalid(form)

"""

git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/tanzila009/Alijahon.git
git push -u origin main
"""
class HomeListView(ListView):
    model = Category
    template_name = 'apps/home.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        return data

class ProfileView(TemplateView):
    template_name = 'apps/auth/profile.html'

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')

class ProductView(TemplateView):
    template_name = 'apps/category.html'

def  district_list_view(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

def get_districts(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)

