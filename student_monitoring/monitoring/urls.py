from django.urls import path

from . import views

urlpatterns = [
  path('', views.home, name='home'),
  path('signin', views.sign_in, name='signin'),
  path('signout', views.sign_out, name='signout'),
  path('set_settings', views.set_settings, name='set_settings'),
  path('statistics', views.get_statistics, name='statistics'),
]
