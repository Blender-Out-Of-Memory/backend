# models.py
from django.db import models

downloadReady = False

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

class WaitForDownload(models.Model):
    download_path = models.FilePathField("")