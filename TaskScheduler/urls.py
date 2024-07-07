from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import RenderTaskViewSet

router = DefaultRouter()
router.register(r'render-tasks', RenderTaskViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
