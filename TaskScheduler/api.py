from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpRequest, HttpResponse
from .models import RenderTask
from .serializers import RenderTaskSerializer
from .TaskScheduler import TaskScheduler

class RenderTaskViewSet(viewsets.ModelViewSet):
    queryset = RenderTask.objects.all()
    serializer_class = RenderTaskSerializer

    @action(detail=False, methods=['post'])
    def run_task(self, request: HttpRequest):
        taskInfo = TaskScheduler.init_new_task()
        if not taskInfo:
            return Response({'error': 'Failed to initialize new task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        taskID, filePath = taskInfo
        with open(filePath, 'wb') as file:
            file.write(request.body)

        success = TaskScheduler.run_task(taskID)
        if success:
            return Response({'Task-ID': taskID}, status=status.HTTP_200_OK)

        return Response({'Error': 'Failed to start task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
