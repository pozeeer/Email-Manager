from django.urls import path
from .views import AddEmailView,email_list

urlpatterns = [
    path('',AddEmailView.as_view(),name='add_email'),
    path('emails',email_list,name='f')
]