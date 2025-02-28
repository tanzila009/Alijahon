from django.urls import path, include

from apps.views import AuthView, HomeListView, ProfileView, LogoutView, ProductView, district_list_view, get_districts

urlpatterns = [
       path("", AuthView.as_view(), name='login'),
    path('home', HomeListView.as_view(), name = 'home'),
    path('profile', ProfileView.as_view(), name= 'profile'),
    path('logut', LogoutView.as_view(), name= 'logout'),
    path('category', ProductView.as_view(), name= 'category'),
    path('district-list', district_list_view, name= 'district-list'),
    path('get_districts', get_districts, name='get_districts'),

    ]