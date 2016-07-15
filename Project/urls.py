"""Project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from chess_tournament.urls import views

auth_urlpatterns = [
    url(r'^auth/(?P<evt>\w+)/(?P<uidb64>[0-9A-Za-z_\-\:]+)?/?(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})?/?', views.auth, name='auth'),
	url(r'^auth/', views.auth, name='auth'),
]

urlpatterns = [
	url(r'^', include(auth_urlpatterns, namespace="chtor_adm")),
	url(r'^', include('chess_tournament.urls', namespace="chtor")),
    url(r'^admin/', admin.site.urls),
]