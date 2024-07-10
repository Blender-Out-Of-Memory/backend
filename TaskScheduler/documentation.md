# TaskScheduler System Documentation

## Overview

The TaskScheduler system is designed to manage and execute rendering tasks for Blender projects. It provides functionality to read Blender files, extract relevant rendering information, queue tasks, and manage their execution.

## Key Components

### 1. BlendFile

The `BlendFile` class is responsible for parsing and extracting information from Blender (.blend) files.

#### Key Features:
- Reads and parses the complex structure of Blender files.
- Extracts all relevant information (and more) for rendering

#### Main Classes:
- **Header**: Represents the file header: Only (maybe) relevant information: File version
- **Scene**: Represents a Blender scene with render settings.

#### Usage:
Only relevant method for simplification:
```python
current_scene = BlendFile.get_current_scene(filepath)
```

### 2. RenderTask

`RenderTask` is a Django model that represents a single rendering task.

#### Fields:
- **TaskID**: Unique identifier for the task
- **FileServerAddress**: URL of the file server
- **FileServerPort**: Port of the file server
- **dataType**: Type of Blender data (single file or multi-file), database field
- **DataType**: Counterpart for previous field for use in Python
- **outputType**: Render output format
- **OutputType**: Counterpart for previous field for use in Python
- **StartFrame**, **EndFrame**, **FrameStep**: Frame range information
- **stage**: Stage of this render task
- **Stage**: Counterpart for previous field for use in Python

#### Methods:
- **progress_simple()**
  - Description: Get summary of progress
  - Return value: Tuple (Stage of RenderTask, Current Stage Progress, Total Progress)
  - Hint: Current Stage Progress is -\infty if doesn't makes sense in current stage
- **progress_detailed()**
  - Description: Get progress by Worker
  - Return value: List of tuples (Portion of total RenderTask assigned to Worker, Worker progress)
  - Hint: Calling only necessary if in distributed stage (currently Rendering only)

### 3. TaskScheduler

`TaskScheduler` is a static class that manages the queue of rendering tasks

#### Key Features:
- Initialize new task
- Run task
- Manage task processing
  - Splitting into subtasks for available workers
  - Redistribution in case of issue
  - Merging with FFmpeg

#### Methods:
- **init_new_task()**: Prepares a new task and returns file path (to safe uploaded file to) and task ID
- **run_task(task_id)**: Starts task execution

#### Usage:
```python
file_path, task_id = TaskScheduler.init_new_task()
# upload file to file_path
TaskScheduler.run_task(task_id)
```
## Enums

### RenderOutputType

Defines the various output formats for rendered images/videos. Examples include:
- TARGA
- PNG
- JPEG
- FFMPEG
- etc.

### BlenderDataType

Specifies if the Blender data is a single file or multiple files:
- SingleFile (.blend)
- MultiFile (placeholder for later implementation) (.zip, containing one or multiple .blend files & other resources if not included in .blend files)


## API

The TaskScheduler system provides a REST API for interacting with rendering tasks.

### RenderTaskViewSet

This ViewSet handles API requests related to RenderTasks.

#### Endpoints:

1. **Upload the file**
   - URL: `/api/render-tasks/run_task/`
   - Method: POST
   - Description: Upload file for a rendering task
   - Request Body: Data to be rendered (only single .blend file at the moment)
   - Response:
     - Success: Returns key ("`TaskKey`") referencing the task created (TaskID at the moment)
     - Failure: Returns an error message

2. **Poll progress report** [TO BE DONE]
   - URL: `/api/render-tasks/[TO BE DONE]/[TaskKey]`
   - Method: GET
   - Description: Requests the progress for task of `TaskKey`
   - Response:
     - Success: Progress
     - Failure: Error message

If progress reports finished

3. **Download the file** [TO BE DONE]
   - URL: `/api/render-tasks/[TO BE DONE]/[TaskKey]`
   - Method: GET
   - Description: Requests download of the render result of `TaskKey`
   - Response:
     - Success: Octet-Stream (standard browser file download) transmitting render result
     - Failure: Error message

### Serializers

#### RenderTaskSerializer

This serializer is used to convert RenderTask model instances to JSON representations and vice versa.

Fields:
- All fields from the RenderTask model

## URL Configuration

The `urls.py` file sets up the URL routing for the TaskScheduler API:

- API root: `/api/`
- RenderTask endpoints: `/api/render-tasks/`

## Testing

The `tests.py` file is prepared for writing unit tests for the TaskScheduler system. It's currently empty and ready for test implementations.

`../testing/uploadfile.py` is a script for emulating a client uploading a .blend file

## Django Integration

The TaskScheduler is set up as a Django app:

- `apps.py`: Defines the TaskSchedulerConfig
- `admin.py`: Can be used to register models with the Django admin interface (currently empty)

These components integrate the TaskScheduler into the broader Django project structure, allowing for easy management and scalability.

