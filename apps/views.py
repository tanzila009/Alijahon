from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.hashers import check_password

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
# from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, FormView, ListView, DetailView

from apps.forms import AuthForm, ProfileForm, ChangePasswordForm, OrderForm
from apps.models import User, District, Region, Category, Product, Wishlist, AdminSetting, Order


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


class HomeListView(ListView):
    queryset = Category.objects.all()
    template_name = 'apps/home.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['products'] = Product.objects.all()
        if self.request.user.is_authenticated:
            data['liked_products_id'] = Wishlist.objects.filter(user_id=self.request.user).values_list("product_id",
                                                                                                   flat=True)
        return data


class ProfileFormView(LoginRequiredMixin, FormView):
    form_class = ProfileForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('profile')

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data

    def form_valid(self, form):
        form.update(self.request.user)
        return super().form_valid(form)

    def form_invalid(self, form):
        pass


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('login')


def get_districts(request):
    region_id = request.GET.get('region_id')
    districts = District.objects.filter(region_id=region_id).values('id', 'name')
    return JsonResponse(list(districts), safe=False)


class ChangePasswordView(FormView):
    form_class = ChangePasswordForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        session_password = self.request.user.password
        old_password = form.cleaned_data.get('old')

        # Check if old password matches the current password
        if not check_password(old_password, session_password):
            messages.error(self.request, 'Old password incorrect.')
            return self.form_invalid(form)

        new_password = form.cleaned_data.get('new')
        self.request.user.set_password(new_password)
        self.request.user.save()

        update_session_auth_hash(self.request, self.request.user)

        messages.success(self.request, 'Your password has been changed successfully.')


        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

class ProductListView(ListView):
    queryset = Product.objects.all()
    template_name = 'apps/menus/product-list.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        slug = self.kwargs.get('slug')
        category = Category.objects.filter(slug=slug).first()
        data = super().get_context_data(object_list=object_list, **kwargs)
        products = Product.objects.all()
        if slug != 'all':
            products = products.filter(category=category)
        # ----------- SEARCH ---------------
        query = self.request.GET.get("query")
        if query:
            products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

        data['products'] = products
        # ------------- SEARCH-------------
        data['categories'] = Category.objects.all()
        if self.request.user.is_authenticated:
            data['liked_products_id'] = Wishlist.objects.filter(user_id=self.request.user).values_list("product_id",
                                                                                                   flat=True)
        data['session_category'] = category
        return data

class WishlistView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    def get(self, request, product_id):
        liked = True
        like = Wishlist.objects.filter(product_id=product_id, user=self.request.user)
        if like.exists():
            like.delete()
            liked = False
        else:
            Wishlist.objects.create(product_id=product_id, user=self.request.user)

        return JsonResponse({"liked": liked})


class ProductDetailView(DetailView):
    queryset = Product.objects.all()
    template_name = 'apps/order/product-detail.html'
    slug_url_kwarg = 'slug'
    context_object_name = 'product'

class LikeListView(ListView):
    queryset = Wishlist.objects.all()
    template_name = 'apps/menus/wishlist.html'
    context_object_name = 'products'

    def get_context_data(self, *, object_list=None, **kwargs):
        data =  super().get_context_data(object_list=object_list, **kwargs)
        data['products'] = Product.objects.filter(wishlist__user=self.request.user)
        if self.request.user.is_authenticated:
            data['liked_products_id'] = Wishlist.objects.filter(user_id=self.request.user).values_list("product_id",
                                                                                                   flat=True)
        return data

class OrderFormView(FormView):
    form_class = OrderForm
    template_name = 'apps/order/product-detail.html'
    success_url = reverse_lazy('order')

    def form_valid(self, form):
        form.owner_id = self.request.user.id
        order = form.save()
        deliver_price = AdminSetting.objects.first().deliver_price
        return render(self.request, 'apps/order/success.html', context={"order": order, "deliver_price": deliver_price})

    def form_invalid(self, form):
        pass

class ProductSearchView(View):
    def post(self, request):
        query = request.GET.get('query')
        products = Product.objects.filter(Q(name__icontains=query) |Q(description__icontains = query))
        return render(request, '')


class OrderListView(ListView):
    login_url = reverse_lazy('login')
    queryset = Order.objects.all()
    template_name = 'apps/order/order-list.html'
    context_object_name = 'orders'

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=object_list, **kwargs)
        data['orders'] = data.get('orders').filter(owner=self.request.user)
        return data



