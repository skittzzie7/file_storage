from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import UserProfile, File
import os
import hashlib

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
        user_profile = UserProfile.objects.get(user=request.user)
        uploaded_file = request.FILES['file']
        file_path = os.path.join(user_profile.folder, uploaded_file.name)
        if os.path.exists(file_path):
            # If file already exists, delete it
            os.remove(file_path)
        with open(file_path, 'wb') as f:
            # Write the uploaded file to disk
            f.write(uploaded_file.read())
            # Calculate the MD5 hash of the file
            md5_hash = hashlib.md5(uploaded_file.read()).hexdigest()
            # Check if any other file in the user's folder has the same MD5 hash
            duplicate_files = File.objects.filter(user_profile=user_profile)
            for file in duplicate_files:
                with open(os.path.join(file_path, file.file.name), 'rb') as f:
                    if md5_hash == hashlib.md5(f.read()).hexdigest():
                        # If duplicate file found, delete the uploaded file and return an error message
                        os.remove(file_path)
                        messages.error(request, "Duplicate file found!")
                        return redirect('home')
            # If no duplicate file found, create a new File object and save it to the database
            file = File(user_profile=user_profile, file=uploaded_file)
            file.save()
            messages.success(request, "File uploaded successfully!")
            return redirect('home')
    else:
        return render(request, 'upload.html')
