from django.conf.urls import url
from analytics import views

urlpatterns = [
    url(r'^log/$', views.log, name='log'),
]

