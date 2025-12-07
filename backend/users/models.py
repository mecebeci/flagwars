from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    
    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
    
    def __str__(self):
        return self.username
