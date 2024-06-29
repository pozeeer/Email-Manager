from django.db import models


class MailServices(models.Model):
    title = models.CharField(max_length=25)
    imap = models.CharField(max_length=15)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "MailServices"


class EmailAccount(models.Model):
    login = models.EmailField(max_length=70)
    email_password = models.CharField(max_length=50)
    imap = models.ForeignKey(MailServices, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = "EmailAccounts"


class LettersInfo(models.Model):
    title = models.CharField(max_length=150, default="AAA", blank=True)
    author = models.CharField(max_length=150,null=True,blank=True)
    receipt_date = models.DateTimeField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    files_list = models.JSONField(blank=True, null=True)
    mail_service = models.ForeignKey(MailServices, on_delete=models.CASCADE, blank=True, default=1)

    class Meta:
        db_table = "LettersInfo"
