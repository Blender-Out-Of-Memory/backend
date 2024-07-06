# TaskScheduler System Documentation

## Overview

The TaskScheduler system is designed to manage and execute rendering tasks for Blender projects. It provides functionality to read Blender files, extract relevant rendering information, queue tasks, and manage their execution.

## Key Components

### 1. BlendFile

The `BlendFile` class is responsible for parsing and extracting information from Blender (.blend) files.

#### Key Features:
- Reads and parses the complex structure of Blender files.
- Extracts scene information, render settings, and other relevant data.
- Handles different Blender file versions and structures.

#### Main Classes:
- **Header**: Represents the file header.
- **BHead**: Represents block headers within the file.
- **SDNA**: Handles the Structure DNA of the Blender file.
- **Scene**: Represents a Blender scene with render settings.

#### Usage:
```python
blend_file = BlendFile.read(filepath)
current_scene = blend_file.CurrentScene
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

