from django.urls import path, include

from apps.views import AuthView, HomeListView, ProfileFormView, LogoutView, ProductListView, get_districts, \
    ChangePasswordView, WishlistView, ProductDetailView, LikeListView, OrderFormView

urlpatterns = [
    path('home', HomeListView.as_view(), name='home'),
    path('products/<str:slug>', ProductListView.as_view(), name='product-list'),
    path('wishlist/<int:product_id>', WishlistView.as_view(), name='wishlist'),
    path('wishlist', LikeListView.as_view(), name='wish-list'),
    path('product/detail/<str:slug>', ProductDetailView.as_view(), name='product-detail'),


]

urlpatterns += [
    path("", AuthView.as_view(), name='login'),

    path('profile', ProfileFormView.as_view(), name='profile'),

    path('logut', LogoutView.as_view(), name='logout'),
    # path('district-list', district_list_view, name= 'district-list'),
    path('get_districts', get_districts, name='get_districts'),
    path('change-password', ChangePasswordView.as_view(), name='change-password'),

]

urlpatterns += [
    path('order/form', OrderFormView.as_view(), name='order')
]