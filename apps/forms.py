
from django.contrib.auth.hashers import make_password
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

