from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import os
import shutil
from typing import Dict, Tuple, List

# Same Django app
from .BlendFile import BlendFile
from .Enums import BlenderDataType, RenderOutputType, TaskStage, SubtaskStage

# Different Django app
from WorkerManager.models import Worker  # must be path from perspective of folder manage.py lies in
# -> different approach: pass class name to foreign key fields

class RenderTask(models.Model):
    TaskID_Int          = models.PositiveSmallIntegerField(primary_key=True)
    TaskID              = models.CharField(max_length=21, unique=True)  # for development
    FileServerAddress   = models.URLField()
    FileServerPort      = models.PositiveIntegerField()  # PositiveSmallIntegerField not possible as range is 0-32k
    DataType            = models.CharField(max_length=5, choices=BlenderDataType)
    OutputType          = models.CharField(max_length=6, null=True, choices=RenderOutputType)
    StartFrame          = models.PositiveIntegerField(null=True)
    EndFrame            = models.PositiveIntegerField(null=True)
    FrameStep           = models.PositiveIntegerField(null=True)
    Stage               = models.CharField(max_length=5, choices=TaskStage)

    # Metadata
    CreatedBy          = models.ForeignKey(User, null=True, blank=True, default=None, on_delete=models.CASCADE)
    StartedAt           = models.DateTimeField(default=timezone.now)
    FinishedAt          = models.DateTimeField(null=True)

    ### Metadata methods
    def update_finish(self):
        self.FinishedAt = timezone.now()
        self.save()


    ### Functional methods
    def get_folder(self) -> str:
        return os.path.abspath(f"tasks/{self.TaskID}/")

    def get_blender_data_path(self) -> str:
        filename = "blenderdata." + ("blend" if (self.DataType == BlenderDataType.SingleFile) else "zip")
        return f"{self.get_folder()}/{filename}"

    def get_result_path(self) -> str:
        extension = ".zip" if (BlenderDataType(self.DataType) == BlenderDataType.SingleFile) else RenderOutputType(self.OutputType).get_extension()
        return f"{self.get_folder()}/output{extension}"


    def get_all_frames(self) -> List[int]:
        frames = []
        for frame in range(self.StartFrame, self.EndFrame, self.FrameStep):
            frames.append(frame)

        return frames

    def get_unassigned_frames(self) -> List[Tuple[int, int]]:  # list of contiguous frame ranges
        frames = self.get_all_frames()

        subtasks = self.Subtask_set.all()
        for subtask in subtasks:
            stage = SubtaskStage(subtask.Stage)
            upperLimit = subtask.EndFrame if (stage != SubtaskStage.Aborted) else subtask.LastestFrame
            for frame in range(subtask.StartFrame, upperLimit, self.FrameStep):
                frames[frames.index(frame)] = -1

        # for preparation of case: last frame range includes very last frame
        frames.append(-1)

        frame_ranges = []
        start = -1
        for i in range(0, len(frames)):
            if (start == -1 and frames[i] != -1):  # start of contiguous frame range
                start = frames[i]
            elif (start != -1 and frames[i] == -1):  # end of contiguous frame range
                frame_ranges.append((start, frames[i - 1]))
                start = -1

        return frame_ranges


    def is_finished(self) -> bool:
        frames = set(self.get_all_frames())

        subtasks = self.Subtask_set.all()
        for subtask in subtasks:
            stage = SubtaskStage(subtask.Stage)
            if stage not in (SubtaskStage.Aborted, SubtaskStage.Finished):
                continue

            upperLimit = subtask.EndFrame if ((stage != SubtaskStage.Aborted)) else subtask.LastestFrame
            for frame in range(subtask.StartFrame, upperLimit, self.FrameStep):
                frames = frames - {frame}

        return not bool(frames)  # true if set is empty

    def progress_simple(self) -> Tuple[TaskStage, float, float]:  # (TaskStage, current stage progress, total progress)
        current_stage = TaskStage(self.Stage)
        totalProgress = current_stage.base_progress()

        if (current_stage.as_number() >= TaskStage.Finished.as_number()):
            if self.FinishedAt is None:
                self.update_finish

            currentStageProgress = 1.0

        if (current_stage == TaskStage.Concatenating):
            currentStageProgress = 0.0  # to be done

        if (current_stage == TaskStage.Rendering):
            subtasks = self.Subtask_set.all()
            currentStageProgress = 0.0
            for subtask in subtasks:
                currentStageProgress += subtask.progress_weighted()

        if (current_stage == TaskStage.Distributing):
            currentStageProgress = 0.0  # to be done

        if (current_stage == TaskStage.Pending):
            currentStageProgress = float("-inf")  # alternatively show progress in pending tasks queue

        if (current_stage == TaskStage.Uploading):
            currentStageProgress = 0.0  # to be done

        currentStageProgress = max(1.0, currentStageProgress)
        totalProgress += currentStageProgress / 3
        finishedAt = self.FinishedAt

        return (current_stage, currentStageProgress, totalProgress, finishedAt)

    def progress_detailed(self) -> List[Tuple[float, float]]:  # array of (portion, progress)
        report = []
        if (TaskStage(self.Stage) == TaskStage.Rendering):
            subtasks = self.Subtask_set.all()
            for subtask in subtasks:
                report.append((subtask.Portion, subtask.progress()))

        return report


    @classmethod
    def create(cls, taskID_int: int, taskID: str, fileServerAddress: str, fileServerPort: int, dataType: BlenderDataType, user: User):
        task_folder = f"tasks/{taskID}"

        try:
            if os.path.exists(task_folder):
                shutil.rmtree(task_folder)
        except Exception as ex:
            print("ERROR: Failed to remove task folder (that shouldn't exist btw)")
            print(ex)
            return None

        try:
            os.makedirs(task_folder, exist_ok=False)
        except:
            print("ERROR: Failed to create new folder for new task")
            return None

        instance = cls(TaskID_Int=taskID_int, TaskID=taskID, FileServerAddress=fileServerAddress, FileServerPort=fileServerPort, DataType=dataType, Stage=TaskStage.Uploading, CreatedBy=user)
        instance.save()
        return instance

    def complete(self) -> bool:
        scene = BlendFile.get_current_scene(self.get_blender_data_path())
        if (scene is None):
            return False

        self.StartFrame = scene.StartFrame
        self.EndFrame   = scene.EndFrame
        self.FrameStep  = scene.FrameStep
        self.Stage      = TaskStage.Pending

        self.OutputType = RenderOutputType.from_scene(scene)

        self.save()

        return True

    # do not define custom constructor, models.Model's constructor must be called to init valid db object
    # might work somehow, but unclean


class Subtask(models.Model):
    SubtaskIndex    = models.PositiveBigIntegerField(primary_key=True)
    Task            = models.ForeignKey(RenderTask, on_delete=models.CASCADE, related_name="Subtask_set")  # is CASCADE right ??
    Worker          = models.ForeignKey("WorkerManager.Worker", on_delete=models.CASCADE)           # is CASCADE right ??
    StartFrame      = models.PositiveIntegerField()
    EndFrame        = models.PositiveIntegerField()
    LastestFrame    = models.PositiveIntegerField(null=True)
    Portion         = models.FloatField()   # Portion of entire Task, relevant for total progres
                                            # Alternatively recalculate it each time in super task
                                            # TODO: change if Subtask completes partially only
    Stage           = models.CharField(max_length=5, choices=SubtaskStage, default=SubtaskStage.Pending)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["SubtaskIndex", "Task"], name='SubtaskIndex-TaskID-UniqueConstraint')
        ]

    def to_headers(self) -> Dict:
        return {
            "Task-Id":              self.Task.TaskID,
            "Subtask-Index":        self.SubtaskIndex,
            "File-Server-Address":  self.Task.FileServerAddress,
            "File-Server-Port":     self.Task.FileServerPort,
            "Blender-Data-Type":    self.Task.DataType,
            "Output-Type":          self.Task.OutputType,
            "Start-Frame":          self.StartFrame,
            "End-Frame":            self.EndFrame,
            "Frame-Step":           self.Task.FrameStep,
        }

    def progress(self) -> float:
        totalFrames = (self.EndFrame - self.StartFrame) / self.Task.FrameStep + 1
        framesDone = (self.LastestFrame - self.StartFrame) / self.Task.FrameStep + 1
        return framesDone / totalFrames

    def progress_weighted(self) -> float:
        return self.progress() * self.Portion

