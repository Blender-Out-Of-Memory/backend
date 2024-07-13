from django.urls import path

from .WorkerManager import WorkerManager as Manager

urlpatterns = [
    path("register", Manager.register, name="register"),
    path("unregister", Manager.unregister, name="unregister"),
]