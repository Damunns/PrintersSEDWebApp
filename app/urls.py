"""
Definition of urls for PrintersSEDWebApp.
"""

from datetime import datetime
from django.urls import path
from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from app import forms, views


urlpatterns = [
    path('', views.home, name='home'),
    path('login/',
         LoginView.as_view
         (
             template_name='app/login.html',
             authentication_form=forms.BootstrapAuthenticationForm,
             extra_context=
             {
                 'title': 'Log in',
                 'year' : datetime.now().year,
             }
         ),
         name='login'),

    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('admin/', admin.site.urls),
    path('update_printer/<printer_id>/', views.update_printer, name='update_printer'),
    path('add_printer/', views.add_printer, name='add_printer'),
    path('delete_printer/<printer_id>/', views.delete_printer, name='delete_printer'),
]
