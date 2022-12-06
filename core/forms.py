from django import forms
from .models import Buy, Client
from django.contrib.auth.models import User



class BuyModelForm(forms.ModelForm):

    class Meta:
        model = Buy
        fields = ['recipient', 'email', 'address']


class DeliveryForm(forms.Form):
    cep = forms.CharField(widget=forms.TextInput)

    class Meta:
        fields = ['cep']

    def clean_cep(self):
        cep = self.cleaned_data.get('cep')

        if len(cep) != 8 or not cep.isdigit():
            raise forms.ValidationError('Erro')
        
        return cep


class RegisterClientModelForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    email = forms.CharField(widget=forms.EmailInput)

    class Meta:
        model = Client
        fields = ['username', 'password', 'email', 'address', 'name']

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists(): 
            raise forms.ValidationError('Este usuário já existe!')

        return username


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    page = forms.CharField(widget=forms.HiddenInput, required = False)

    class Meta:
        fields = ['username', 'password']