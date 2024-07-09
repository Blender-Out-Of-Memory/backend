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
- **Header**: Represents the file header: Only relevant information: File version
- **Scene**: Represents a Blender scene with render settings.

#### Usage:
```python
current_scene = BlendFile.get_current_scene(filepath)
```

### 2. RenderTask

`RenderTask` is a Django model that represents a single rendering task.

#### Fields:
- **TaskID**: Unique identifier for the task.
- **FileServerAddress**: URL of the file server.
- **FileServerPort**: Port of the file server.
- **dataType**: Type of Blender data (single file or multi-file).
- **outputType**: Render output format.
- **StartFrame**, **EndFrame**, **FrameStep**: Frame range information.

#### Methods:
- **get_folder()**: Returns the task's folder path.
- **get_filename()**: Returns the Blender file name.
- **to_headers()**: Converts task information to HTTP headers.

#### Usage:
```python
task = RenderTask.create(task_id, file_server_address, file_server_port, data_type)
```

### 3. TaskScheduler

`TaskScheduler` is a static class that manages the queue of rendering tasks.

#### Key Features:
- Initializes new tasks.
- Manages task queues (normal and high priority).
- Handles task execution.

#### Methods:
- **init_new_task()**: Prepares a new task and returns file path and task ID.
- **run_task(task_id, progress_callback, finished_callback)**: Starts task execution.

#### Usage:
```python
file_path, task_id = TaskScheduler.init_new_task()
TaskScheduler.run_task(task_id, progress_callback, finished_callback)
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
- SingleFile
- MultiFile

## Workflow

1. **Initialize a new task:**
    ```python
    file_path, task_id = TaskScheduler.init_new_task()
    ```

2. **Upload the Blender file to the provided file_path.**

3. **Start the rendering task:**
    ```python
    TaskScheduler.run_task(task_id, progress_callback, finished_callback)
    ```

The system will handle the task execution, calling the provided callbacks for progress updates and task completion.

## API

The TaskScheduler system provides a REST API for interacting with rendering tasks.

### RenderTaskViewSet

This ViewSet handles API requests related to RenderTasks.

#### Endpoints:

1. **Initialize New Task**
   - URL: `/api/render-tasks/init_new_task/`
   - Method: POST
   - Description: Initializes a new rendering task
   - Response:
     - Success: Returns file path and task ID
     - Failure: Returns an error message

   Example usage:
   ```python
   response = requests.post('/api/taskscheduler/render-tasks/init_new_task/')
   if response.status_code == 200:
       file_path, task_id = response.json()['file_path'], response.json()['task_id']
    ```
3. **Run Task**
   - URL: `/api/render-tasks/run_task/`
   - Method: POST
   - Description: Starts the execution of a rendering task
   - Request Body: JSON object with `task_id`
   - Response:
     - Success: Confirmation message
     - Failure: Error message

   Example usage:
   ```python
   response = requests.post('/api/taskscheduler/render-tasks/run_task/', json={'task_id': 'task_123'})
   if response.status_code == 200:
       print("Task started successfully")
    ```
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

## Django Integration

The TaskScheduler is set up as a Django app:

- `apps.py`: Defines the TaskSchedulerConfig
- `admin.py`: Can be used to register models with the Django admin interface (currently empty)

These components integrate the TaskScheduler into the broader Django project structure, allowing for easy management and scalability.

