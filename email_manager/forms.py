from django import forms

from .models import MailServices, EmailAccount


class EmailAccountForm(forms.ModelForm):
    email_service = forms.ModelChoiceField(
        queryset=MailServices.objects.all(),
        widget=forms.Select(),
    )
    class Meta:
        model = EmailAccount
        fields = ('login', 'email_password', 'email_service')
        widgets = {
            'login':forms.TextInput(),
            'email_password':forms.PasswordInput
        }