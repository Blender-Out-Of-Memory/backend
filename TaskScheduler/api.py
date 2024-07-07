from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import RenderTask
from .serializers import RenderTaskSerializer
from .TaskScheduler import TaskScheduler

class RenderTaskViewSet(viewsets.ModelViewSet):
    queryset = RenderTask.objects.all()
    serializer_class = RenderTaskSerializer

    @action(detail=False, methods=['post'])
    def init_new_task(self, request):
        result = TaskScheduler.init_new_task()
        if result:
            file_path, task_id = result
            return Response({'file_path': file_path, 'task_id': task_id})
        return Response({'error': 'Failed to initialize new task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'])
    def run_task(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        def progress_callback(progress):
            pass

        def finished_callback(result):
            pass

        success = TaskScheduler.run_task(task_id, progress_callback, finished_callback)
        if success:
            return Response({'message': 'Task started successfully'})
        return Response({'error': 'Failed to start task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
