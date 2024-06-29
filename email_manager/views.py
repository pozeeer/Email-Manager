from django.shortcuts import render
from django.views import View

from .forms import EmailAccountForm
from .models import EmailAccount, MailServices


class AddEmailView(View):
    def get(self, request):
        form = EmailAccountForm()
        return render(request, "email_manager/add_email_acc.html", context={'form': form})

    def post(self, request):
        form: EmailAccountForm = EmailAccountForm(request.POST)
        form_data = form.data
        account = EmailAccount(
            login=form_data.get('login'), email_password=form_data.get('email_password'),
            imap=MailServices.objects.get(id=form_data.get('email_service'))
        )
        account.save()
        return render(request, 'email_manager/emails.html')


def email_list(request):
    # emails = LettersInfo.objects.all()
    return render(request, 'email_manager/emails.html', )
