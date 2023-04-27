from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

from file_storage_project import settings
from .models import UserProfile, File
import os
import hashlib

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UploadFileForm
from .models import UserFile


def home(request):
    if request.user.is_authenticated:
        user_profile = UserProfile.objects.get(user=request.user)
        folder = user_profile.folder
        files = File.objects.filter(user_profile=user_profile)
        return render(request, 'home.html', {'folder': folder, 'files': files})
    else:
        return redirect('login')

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('signup')
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user_profile = UserProfile(user=user)
            user_profile.folder = os.path.join('user_files', str(user_profile.user_id))
            os.makedirs(user_profile.folder, exist_ok=True)
            user_profile.save()
            messages.success(request, "User created successfully!")
            return redirect('login')
        except:
            messages.error(request, "An error occurred while creating the user")
            return redirect('signup')
    else:
        return render(request, 'signup.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    else:
        return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            user_file = form.cleaned_data['user_file']
            md5sum = user_file.read()
            user_file.seek(0)
            md5sum = hashlib.md5(md5sum).hexdigest()
            user = request.user
            path = os.path.join(settings.MEDIA_ROOT, str(user.id))
            if not os.path.exists(path):
                os.mkdir(path)
            path = os.path.join(path, md5sum + '_' + user_file.name)
            if not os.path.exists(path):
                with open(path, 'wb+') as destination:
                    for chunk in user_file.chunks():
                        destination.write(chunk)
                messages.success(request, 'Your file was successfully uploaded.')
                UserFile.objects.create(user=user, file=path)
            else:
                messages.error(request, 'A file with the same name already exists.')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})
