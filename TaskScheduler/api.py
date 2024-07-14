from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse
from .models import RenderTask
from .serializers import RenderTaskSerializer
from .TaskScheduler import TaskScheduler

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user

class RenderTaskViewSet(viewsets.ModelViewSet):
    queryset = RenderTask.objects.all()
    serializer_class = RenderTaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return RenderTask.objects.filter(created_by=self.request.user)

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(RenderTaskViewSet, self).get_permissions()

    @action(detail=False, methods=['post'])
    def run_task(self, request: HttpRequest):
        taskInfo = TaskScheduler.init_new_task(request.user)
        if not taskInfo:
            return Response({'error': 'Failed to initialize new task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        taskID, filePath = taskInfo
        with open(filePath, 'wb') as file:
            file.write(request.body)
        try:
            success = TaskScheduler.run_task(taskID)
            if success:
                return Response({'message': 'Task started successfully'})
            return Response({'error': 'Failed to start task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except RenderTask.DoesNotExist:
            return Response({'error': f'Task with ID {task_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
