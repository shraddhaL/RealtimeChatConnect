from gettext import translation
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

class UserManager(BaseUserManager):
    def _create_user(self, username, password, **extra_fields):
        """ 
    Creates and saves a User with the username email,and password. 
    """
        if not username:
            raise ValueError('The given username must be set')
        try:
            with translation.atomic():
                user = self.model(username=username, **extra_fields)
                user.set_password(password)
                user.save(using=self._db)
                return user
        except:
            raise

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password=password, **extra_fields)
    
class CustomUser(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
     
    USERNAME_FIELD = 'username'

    objects = UserManager()
    
    def __str__(self):
        return self.username
    
    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        return self
    


