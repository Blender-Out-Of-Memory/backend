from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name='index'),
    path("file_upload/", views.upload_file, name='upload_file'),
    path("wait/", views.wait, name='waiting'),
    path("upload/success/", views.upload_success, name='file_upload_success'),
]