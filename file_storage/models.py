from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    folder = models.CharField(max_length=255, blank=True)

class File(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    file = models.FileField(upload_to='user_files/')
