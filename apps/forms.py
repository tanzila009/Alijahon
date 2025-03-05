
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import CharField, IntegerField
from django.forms.forms import Form
from django.forms.models import ModelForm
from apps.models import User

class AuthForm(Form):
    phone_number = CharField(max_length=20)
    password = CharField(max_length=255)

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return make_password(password)

class LoginForm(Form):
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    district_id = CharField(required=False)
    address = CharField(required=False)
    telegram_id = IntegerField(required=False)

class ProfileForm(LoginRequiredMixin, Form):
    first_name = CharField(required=False)
    last_name = CharField(required=False)
    district_id = CharField(required=False)
    address = CharField(required=False)
    telegram_id = IntegerField(required=False)
    about = CharField(required=False)

    def update(self, user):
        data = {key: values for key, values in self.cleaned_data.items() if values not in [None, ""]}
        if data:
            User.objects.filter(pk=user.pk).update(**data)

class ChangePasswordForm(Form):
    old = CharField(required=False)
    new = CharField(required=False)
    confirm = CharField(required=False)

    def clean_confirm(self):
        new = self.cleaned_data.get('new')
        confirm = self.cleaned_data.get('confirm')
        if new != confirm:
            raise ValidationError("The new password does not match the old one.")

    def clean_new(self):
        return make_password(self.cleaned_data.get('new'))

    def update(self , user):
        password = self.cleaned_data.get('new')
        User.objects.filter(pk=user.id).update(password=password)