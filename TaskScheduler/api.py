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

        file_path, task_id = taskInfo
        with open(file_path, 'wb') as file:
            file.write(request.body)

        print("bef run task")
        success = TaskScheduler.run_task(task_id)
        print("After run task")
        if success:
            return Response({'message': 'Task started successfully'})
        return Response({'error': 'Failed to start task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
