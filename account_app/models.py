from typing import Any
from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import PermissionsMixin
import uuid
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

# Create your models here.
class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password,**extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", 1)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser has to have is_staff being True")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser has to have is_superuser being True")

        return self.create_user(username=username, password=password,**extra_fields)


class Instancy(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    balai_name = models.CharField(max_length=50)

    def __str__(self):
        return self.balai_name
    
    class Meta:
        db_table = "instancy"

class User(AbstractUser,PermissionsMixin):
    SUPERADMIN = 1
    ADMIN = 2
    GUEST = 3
    QA = 4

    ROLE_CHOICES = (
        (SUPERADMIN, 'SuperAdmin'),
        (ADMIN, 'Admin'),
        (GUEST, 'Guest'),
        (QA, 'QA')
    )

    instancy =models.ForeignKey(Instancy, on_delete=models.CASCADE, blank=True, null=True)
    uid = models.UUIDField(unique=True, editable=False, default=uuid.uuid4, verbose_name='uid')
    username = models.CharField(max_length=40, unique=True)
    # email = models.EmailField(unique=True)
    # first_name = models.CharField(max_length=30, blank=False,null=False)
    # last_name = models.CharField(max_length=50, blank=False ,null=False)
    role = models.IntegerField (choices=ROLE_CHOICES, default=1)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    modified_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users')

    objects = CustomUserManager()
    USERNAME_FIELD = 'username'
    # REQUIRED_FIELDS =['email','role']


    def __str__(self):
        return self.username



@receiver(pre_save, sender=User)
def update_modified_time(sender, instance, **kwargs):
    instance.modified_at = timezone.now()

