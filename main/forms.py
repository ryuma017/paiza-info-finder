from django import forms

class PaizaAuthenticationForm(forms.Form):
    email = forms.EmailField(max_length=100, label='email', required=True)
    password = forms.CharField(max_length=100, label='password', widget=forms.PasswordInput(), required=True)
