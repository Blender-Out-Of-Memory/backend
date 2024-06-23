from threading import Thread

from django.shortcuts import render, redirect
from .forms import UploadFileForm
from .models import UploadedFile

from ..TaskScheduler import deleteme

def index(request):
    form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('../wait/')

def upload_success(request):
    return render(request, 'upload_success.html')

def unlock_download():
    pass

def wait(request):
    delayer = Thread(target=deleteme, args=(unlock_download))
    delayer.start()
    return render(request, 'wait.html')