from django.contrib import admin

from .models import *


# class MailServicesAdmin(admin.ModelAdmin):
#     list_display = ('id', 'title', 'imap')
#     list_display_links = ('id', 'title')
#
#     class Meta:
#         verbose_name = 'Почтовый сервис'
#         verbose_name_plural = 'Почтовые сервисы'


class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'login','imap_id')
    list_display_links = ('id', 'login')

    class Meta:
        verbose_name = 'Почтовый аккаунт'
        verbose_name_plural = 'Почтовые аккаунты'


class LettersInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'files_list')
    list_display_links = ('id', 'title')

    class Meta:
        verbose_name = 'Информация о письме'
        verbose_name_plural = 'Информация о письмах'


admin.site.register(MailServices)
admin.site.register(EmailAccount, EmailAccountAdmin)
admin.site.register(LettersInfo, LettersInfoAdmin)
