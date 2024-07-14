from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest, HttpResponse, FileResponse
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import RenderTask
from .serializers import RenderTaskSerializer
from .TaskScheduler import TaskScheduler
import os


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.CreatedBy == request.user


class RenderTaskViewSet(viewsets.ModelViewSet):
    queryset = RenderTask.objects.all()
    serializer_class = RenderTaskSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(CreatedBy=self.request.user)

    def get_queryset(self):
        return RenderTask.objects.filter(CreatedBy=self.request.user)

    def get_permissions(self):
        if self.action in ["retrieve", "update", "partial_update", "destroy"]:
            self.permission_classes = [IsAuthenticated, IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(RenderTaskViewSet, self).get_permissions()

    @action(detail=True, methods=["get"], url_path="download")
    def download_file(self, request, pk=None):
        job = self.get_object()
        path = job.get_result_path()
        print(path)

        if os.path.exists(path):
            response = FileResponse(open(path, "rb"))
            response["Content.Disposition"] = (
                f'attachment; filename="{os.path.basename(path)}"'
            )
            return response
        else:
            return HttpResponse("File not found", status=404)

    @action(detail=True, methods=["get"], url_path="job-progress")
    def job_progress(self, request, pk=None):
        job = self.get_object()
        stage, currentStageProgress, totalProgress, finishedAt = job.progress_simple()
        return Response(
            {
                "Stage": stage,
                "currentStageProgress": currentStageProgress,
                "totalProgress": totalProgress,
                "finishedAt": finishedAt
            }
        )

    @action(detail=False, methods=["post"])
    def run_task(self, request: HttpRequest):
        taskInfo = TaskScheduler.init_new_task(request.user)
        if not taskInfo:
            return Response({'error': 'Failed to initialize new task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        taskID, filePath = taskInfo
        with open(filePath, "wb") as file:
            file.write(request.body)

        success = TaskScheduler.run_task(taskID)
        if success:
            return Response({'Task-ID': taskID}, status=status.HTTP_200_OK)

        return Response({'Error': 'Failed to start task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
