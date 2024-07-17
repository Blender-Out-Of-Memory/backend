from django.urls import path

from .WorkerManager import WorkerManager as Manager

urlpatterns = [
    path("register/", Manager.register, name="register"),
    path("unregister/", Manager.unregister, name="unregister"),
    path("post-render-result/", Manager.receive_result, name="receive_result"),
    path("download-blender-data/", Manager.download_blender_data, name="download_blender_data")
]