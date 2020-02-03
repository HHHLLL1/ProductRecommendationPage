from django.conf.urls import url
from login import views
from django.urls import path, include


app_name = 'front'

urlpatterns = [
    path('index/<item_id>', views.detail, name='detail'),
]

