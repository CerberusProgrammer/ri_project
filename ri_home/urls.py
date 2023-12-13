from django.urls import path, include

from ri_home.views import home

urlpatterns = [
    path('', home, name='home'),
]
